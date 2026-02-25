import os.path as pth

import numpy as np
from fastoad.constants import EngineSetting
from fastoad.io import VariableIO
from fastoad.model_base import FlightPoint

from ..ml_tp_l1 import ML_TP_L1

DATA_FOLDER_PATH = pth.join(pth.dirname(__file__), "data")
RESULTS_FOLDER_PATH = pth.join(pth.dirname(__file__), "results")
CONFIGURATION_FILE = "oad_sizing.toml"
SOURCE_FILE = "problem_outputs.xml"
RESULTS_FOLDER = "problem_folder"

engine_params = {
    "RTO_power": "data:propulsion:RTO_power",
    "power_offtake": "data:propulsion:power_offtake",
    "gearbox_eta": "data:propulsion:gearbox_eta",
    "d_prop": "data:geometry:propulsion:propeller:diameter",
    "k_gb_RTO": "settings:propulsion:ratings:RTO:k_gb",
    "k_gb_NTO": "settings:propulsion:ratings:NTO:k_gb",
    "k_gb_MCL": "settings:propulsion:ratings:MCL:k_gb",
    "k_gb_MCR": "settings:propulsion:ratings:MCR:k_gb",
    "k_psfc": "tuning:propulsion:k_psfc",
    "k_prop": "tuning:propulsion:k_prop",
}


def test_ML_TP_L1():
    var_name = []
    for var, name in engine_params.items():
        var_name.append(name)

    input_data = VariableIO(pth.join(DATA_FOLDER_PATH, SOURCE_FILE)).read(only=var_name)

    argument = {}
    for var, name in engine_params.items():
        argument[var] = input_data[name].value[0]

    engine = ML_TP_L1(**argument)

    # Test scalar
    flight_point = FlightPoint(
        mach=0.45,
        altitude=6096,
        engine_setting=EngineSetting.CRUISE,
        thrust=7250,
        thrust_is_regulated=1.0,
    )  # with engine_setting as int
    engine.compute_flight_points(flight_point)
    np.testing.assert_allclose(flight_point.psfc, 8.43e-8, rtol=1e-3)
    np.testing.assert_allclose(flight_point.thrust_rate, 0.832, rtol=1e-3)

    flight_point = FlightPoint(
        mach=0, altitude=0, engine_setting=EngineSetting.TAKEOFF, thrust_rate=0.8
    )  # with engine_setting as EngineSetting
    engine.compute_flight_points(flight_point)
    np.testing.assert_allclose(flight_point.psfc, 9.253e-8, rtol=1e-3)
    np.testing.assert_allclose(flight_point.thrust, 31605, rtol=1e-3)

    flight_point = FlightPoint(
        mach=0.3,
        altitude=3000,
        engine_setting=EngineSetting.CLIMB.value,
        thrust_rate=1.0,
    )  # with engine_setting as int
    engine.compute_flight_points(flight_point)
    np.testing.assert_allclose(flight_point.thrust, 14293, rtol=1e-3)
    np.testing.assert_allclose(flight_point.psfc, 8.216e-8, rtol=1e-3)
    np.testing.assert_allclose(flight_point.sfc, 9.323e-6, rtol=1e-3)
    np.testing.assert_allclose(flight_point.TPshaft_power, 1.621e6, rtol=1e-3)

    # Test disa
    flight_point = FlightPoint(
        mach=0.3,
        altitude=3000,
        engine_setting=EngineSetting.CLIMB.value,
        thrust_rate=1.0,
        isa_offset=15,
    )  # with engine_setting as int
    engine.compute_flight_points(flight_point)
    np.testing.assert_allclose(flight_point.thrust, 13584.3, rtol=1e-3)
    np.testing.assert_allclose(flight_point.psfc, 8.216e-8, rtol=1e-3)
    np.testing.assert_allclose(flight_point.sfc, 9.551e-6, rtol=1e-3)
    np.testing.assert_allclose(flight_point.TPshaft_power, 1.579e6, rtol=1e-3)
