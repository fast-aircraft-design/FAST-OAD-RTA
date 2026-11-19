import contextlib
from pathlib import Path
from shutil import rmtree

import numpy as np
import openmdao.api as om
import pandas as pd
import pytest
from fastoad import api
from fastoad.io import VariableIO
from fastoad.io.configuration.configuration import FASTOADProblemConfigurator
from fastoad.module_management._plugins import FastoadLoader
from numpy.testing import assert_allclose

FastoadLoader()


DATA_FOLDER_PATH = Path(__file__).parent / "data"
RESULTS_FOLDER_PATH = Path(__file__).parent / "results"
CONFIGURATION_FILE = "oad_process.yml"
MISSION_FILE = "sizing_mission_R.yml"
SOURCE_FILE = "problem_outputs.xml"
RESULTS_FOLDER = "problem_folder"


@pytest.fixture(scope="module")
def cleanup():
    rmtree(RESULTS_FOLDER_PATH, ignore_errors=True)


def test_non_regression_mission(cleanup):
    run_non_regression_test(
        CONFIGURATION_FILE,
        SOURCE_FILE,
        RESULTS_FOLDER,
        check_only_mtow=False,
        tolerance=1.0e-2,
    )


def run_non_regression_test(
    conf_file,
    legacy_result_file,
    result_dir,
    *,
    check_only_mtow=False,
    tolerance=5.0e-3,
):
    results_folder_path = RESULTS_FOLDER_PATH / result_dir
    source_data_path = RESULTS_FOLDER_PATH / "source_problem_inputs_rta.xml"
    configuration_file_path = results_folder_path / conf_file
    mission_file_path = results_folder_path / "sizing_mission_R.yml"

    # Copy of configuration file, mission file and generation of problem instance ------------------
    api.generate_configuration_file(
        configuration_file_path,
        distribution_name="FAST-OAD-RTA",
        overwrite=True,
        sample_file_name="oad_process.yml",
    )
    # We can actually use the same command to copy the mission file
    api.generate_configuration_file(
        mission_file_path,
        distribution_name="FAST-OAD-RTA",
        overwrite=True,
        sample_file_name="sizing_mission_R.yml",
    )
    # Copy source data file
    api.generate_source_data_file(
        source_data_path, distribution_name="FAST-OAD-RTA", overwrite=True
    )
    api.generate_inputs(configuration_file_path, source_data_path=source_data_path, overwrite=True)
    configurator = FASTOADProblemConfigurator(configuration_file_path)

    # Generation and reading of inputs ----------------------------------------
    problem = configurator.get_problem()
    problem.read_inputs()
    problem.setup()

    # Run model ---------------------------------------------------------------
    problem.run_model()
    problem.write_outputs()

    with contextlib.suppress(AttributeError):
        problem.model.performance.flight_points.to_csv(
            results_folder_path / "flight_points.csv",
            sep="\t",
            decimal=",",
        )

    om.view_connections(
        problem,
        outfile=(results_folder_path / "connections.html").as_posix(),
        show_browser=False,
    )

    # Check that weight-performances loop correctly converged
    assert_allclose(
        problem.get_val("data:weight:aircraft:OWE", units="kg"),
        problem.get_val("data:weight:airframe:mass", units="kg")
        + problem.get_val("data:weight:propulsion:mass", units="kg")
        + problem.get_val("data:weight:systems:mass", units="kg")
        + problem.get_val("data:weight:furniture:mass", units="kg")
        + problem.get_val("data:weight:operational:mass", units="kg"),
        atol=1,
    )
    assert_allclose(
        problem.get_val("data:weight:aircraft:MZFW", units="kg"),
        problem.get_val("data:weight:aircraft:OWE", units="kg")
        + problem.get_val("data:weight:aircraft:max_payload", units="kg"),
        atol=1,
    )

    ref_var_list = VariableIO(
        DATA_FOLDER_PATH / legacy_result_file,
    ).read()

    row_list = []
    for ref_var in ref_var_list:
        try:
            value = problem.get_val(ref_var.name, units=ref_var.units)[0]
        except KeyError:
            continue
        row_list.append(
            {
                "name": ref_var.name,
                "units": ref_var.units,
                "ref_value": ref_var.value[0],
                "value": value,
            }
        )

    df = pd.DataFrame(row_list)
    df["rel_delta"] = (df.value - df.ref_value) / df.ref_value
    df.loc[(df.ref_value == 0) & (abs(df.value) <= 1e-10), "rel_delta"] = 0.0
    df["abs_rel_delta"] = np.abs(df.rel_delta)

    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 1000)
    pd.set_option("display.max_colwidth", 120)
    print(df.sort_values(by=["abs_rel_delta"]))

    if check_only_mtow:
        assert np.all(df.abs_rel_delta.loc[df.name == "data:weight:aircraft:MTOW"] < tolerance)
    else:
        assert np.all(df.abs_rel_delta < tolerance)
