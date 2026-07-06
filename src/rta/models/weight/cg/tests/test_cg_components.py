"""
Test module for geometry functions of cg components
"""
#  This file is part of RTA
#  Copyright (C) 2025 ONERA & ISAE-SUPAERO
#  FAST is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

# pylint: disable=redefined-outer-name  # needed for pytest fixtures

from pathlib import Path

import openmdao.api as om
import pytest
from fastoad.io import VariableIO
from fastoad.testing import run_system
from openmdao.api import IndepVarComp
from pytest import approx

from ..cg_components.compute_cg_flight_controls import (
    ComputeFlightControlCG,
)
from ..cg_components.compute_cg_loadcase1 import ComputeCGLoadCase1
from ..cg_components.compute_cg_loadcase2 import ComputeCGLoadCase2
from ..cg_components.compute_cg_loadcase3 import ComputeCGLoadCase3
from ..cg_components.compute_cg_loadcase4 import ComputeCGLoadCase4
from ..cg_components.compute_cg_others import ComputeOthersCG
from ..cg_components.compute_cg_ratio_aft import ComputeCGRatioAft
from ..cg_components.compute_max_cg_ratio import ComputeMaxCGratio
from ..cg_components.compute_propulsion_cg import ComputePropulsionCG_RTA


def get_indep_var_comp(var_names):
    """Reads required input data and returns an IndepVarcomp() instance"""
    reader = VariableIO(Path(__file__).parent.resolve() / "data" / "ref_cg.xml")
    reader.path_separator = ":"
    variables = reader.read(only=var_names)
    for variable in variables:
        if variable.units is None:
            variable.units = "unitless"
    return variables.to_ivc()


def test_compute_flight_control_cg():
    """Tests computation of tanks center of gravity"""

    input_vars = om.IndepVarComp()
    input_vars.add_output("data:geometry:wing:MAC:length", 2.277, units="m")
    input_vars.add_output("data:geometry:wing:MAC:y", 6.197, units="m")
    input_vars.add_output("data:geometry:wing:MAC:at25percent:x", 12.628, units="m")
    input_vars.add_output("data:geometry:wing:MAC:leading_edge:x:local", 0.302, units="m")
    input_vars.add_output("data:geometry:wing:kink:chord", 2.4, units="m")
    input_vars.add_output("data:geometry:wing:kink:y", 5.189, units="m")
    input_vars.add_output("data:geometry:wing:kink:leading_edge:x:local", 0.234, units="m")
    input_vars.add_output("data:geometry:wing:root:chord", 2.633, units="m")
    input_vars.add_output("data:geometry:wing:root:y", 1.396, units="m")
    input_vars.add_output("data:geometry:wing:tip:chord", 1.685, units="m")
    input_vars.add_output("data:geometry:wing:tip:leading_edge:x:local", 0.743, units="m")
    input_vars.add_output("data:geometry:wing:tip:y", 13.421, units="m")

    problem = run_system(ComputeFlightControlCG(), input_vars)

    x_cg_flight_control = problem.get_val("data:weight:systems:flight_controls:CG:x", "m")
    assert x_cg_flight_control == pytest.approx(14.365, abs=1e-2)


def test_compute_propulsion_cg():
    input_list = [
        "data:geometry:propulsion:engine:y_ratio",
        "data:geometry:wing:span",
        "data:geometry:wing:MAC:length",
        "data:geometry:wing:MAC:leading_edge:x:local",
        "data:geometry:wing:root:chord",
        "data:geometry:wing:root:y",
        "data:geometry:wing:kink:chord",
        "data:geometry:wing:kink:y",
        "data:geometry:wing:kink:leading_edge:x:local",
        "data:geometry:wing:MAC:at25percent:x",
        "data:geometry:propulsion:nacelle:length",
    ]

    ivc = get_indep_var_comp(input_list)

    problem = run_system(ComputePropulsionCG_RTA(), ivc)

    assert problem.get_val("data:weight:propulsion:engine:CG:x", "m") == approx(11.36, rel=1e-3)
    assert problem.get_val("data:weight:propulsion:propeller:CG:x", "m") == approx(9.657, rel=1e-3)
    assert problem.get_val("data:weight:airframe:nacelle:CG:x", "m") == approx(11.645, rel=1e-3)


def test_compute_loadcase1():
    input_list = [
        "data:geometry:wing:MAC:length",
        "data:geometry:wing:MAC:at25percent:x",
        "data:mission:sizing:fuel",
        "data:weight:fuel_tank:CG:x",
        "data:weight:aircraft:operating_empty:CG:x",
        "data:weight:aircraft:operating_empty:mass",
    ]
    ivc = get_indep_var_comp(input_list)

    problem = run_system(ComputeCGLoadCase1(), ivc)

    assert problem.get_val(
        "data:weight:aircraft:load_case_1:CG:MAC_position",
    ) == approx(0.057, rel=1e-3)
    assert problem.get_val(
        "data:weight:aircraft:load_case_1:CG:index",
    ) == approx(-49.09, rel=1e-3)
    assert problem.get_val("data:weight:aircraft:load_case_1:mass", "kg") == approx(16757, abs=1)


def test_compute_loadcase2():
    input_list = [
        "data:geometry:wing:MAC:length",
        "data:geometry:wing:MAC:at25percent:x",
        "data:weight:payload:rear_fret:CG:x",
        "data:weight:payload:front_fret:CG:x",
        "data:TLAR:NPAX",
        "data:mission:sizing:fuel",
        "data:weight:fuel_tank:CG:x",
        "data:weight:aircraft:operating_empty:CG:x",
        "data:weight:aircraft:operating_empty:mass",
        "settings:weight:aircraft:payload:design_mass_per_passenger",
        "settings:weight:aircraft:payload:fret_ratio",
    ]
    ivc = get_indep_var_comp(input_list)

    problem = run_system(ComputeCGLoadCase2(), ivc)

    assert problem.get_val(
        "data:weight:aircraft:load_case_2:CG:MAC_position",
    ) == approx(0.025, rel=1e-3)
    assert problem.get_val(
        "data:weight:aircraft:load_case_2:CG:index",
    ) == approx(-60.75, rel=1e-3)
    assert problem.get_val("data:weight:aircraft:load_case_2:mass", "kg") == approx(17783, abs=1)


def test_compute_loadcase3():
    input_list = [
        "data:geometry:wing:MAC:length",
        "data:geometry:wing:MAC:at25percent:x",
        "data:weight:payload:PAX:CG:x",
        "data:weight:payload:rear_fret:CG:x",
        "data:weight:payload:front_fret:CG:x",
        "data:mission:sizing:fuel",
        "data:weight:fuel_tank:CG:x",
        "data:TLAR:NPAX",
        "data:weight:aircraft:operating_empty:CG:x",
        "data:weight:aircraft:operating_empty:mass",
        "settings:weight:aircraft:payload:design_mass_per_passenger",
        "settings:weight:aircraft:payload:fret_ratio",
    ]
    ivc = get_indep_var_comp(input_list)

    problem = run_system(ComputeCGLoadCase3(), ivc)

    assert problem.get_val(
        "data:weight:aircraft:load_case_3:CG:MAC_position",
    ) == approx(0.0362, rel=1e-3)
    assert problem.get_val(
        "data:weight:aircraft:load_case_3:CG:index",
    ) == approx(-76.6, rel=1e-3)
    assert problem.get_val("data:weight:aircraft:load_case_3:mass", "kg") == approx(23597, abs=1)


def test_compute_loadcase4():
    input_list = [
        "data:geometry:wing:MAC:length",
        "data:geometry:wing:MAC:at25percent:x",
        "data:weight:payload:PAX:CG:x",
        "data:weight:payload:rear_fret:CG:x",
        "data:weight:payload:front_fret:CG:x",
        "data:TLAR:NPAX",
        "data:weight:aircraft_empty:CG:x",
        "data:weight:aircraft_empty:mass",
    ]
    ivc = get_indep_var_comp(input_list)

    problem = run_system(ComputeCGLoadCase4(), ivc)

    assert problem.get_val(
        "data:weight:aircraft:load_case_4:CG:MAC_position",
    ) == approx(0.1045, rel=1e-3)


def test_compute_cg_others():
    input_list = [
        "data:geometry:wing:MAC:leading_edge:x:local",
        "data:geometry:wing:MAC:length",
        "data:geometry:wing:root:chord",
        "data:geometry:fuselage:length",
        "data:geometry:wing:MAC:at25percent:x",
        "data:geometry:fuselage:front_length",
        "data:geometry:fuselage:rear_length",
        "data:weight:propulsion:engine:CG:x",
        "data:weight:fuel_tank:CG:x",
        "data:weight:operational:items:passenger_seats:CG:x",
        "data:weight:propulsion:engine:mass",
        "data:geometry:cabin:NPAX1",
        "data:geometry:cabin:seats:economical:count_by_row",
        "data:geometry:cabin:seats:economical:length",
    ]
    ivc = get_indep_var_comp(input_list)
    problem = run_system(ComputeOthersCG(), ivc)

    assert problem.get_val("data:weight:airframe:fuselage:CG:x", "m") == approx(12.13, rel=1e-3)
    assert problem.get_val("data:weight:airframe:landing_gear:front:CG:x", "m") == approx(
        3.74, rel=1e-3
    )
    assert problem.get_val(
        "data:weight:propulsion:engine_controls_instrumentation:CG:x", "m"
    ) == approx(2.493, rel=1e-3)
    assert problem.get_val("data:weight:propulsion:fuel_lines:CG:x", "m") == approx(
        12.587, rel=1e-3
    )

    assert problem.get_val("data:weight:systems:auxiliary_power_unit:CG:x", "m") == approx(
        25.6, rel=1e-3
    )
    assert problem.get_val(
        "data:weight:systems:electric_systems:electric_generation:CG:x", "m"
    ) == approx(6.74, rel=1e-3)
    assert problem.get_val(
        "data:weight:systems:electric_systems:electric_common_installation:CG:x", "m"
    ) == approx(6.74, rel=1e-3)
    assert problem.get_val("data:weight:systems:hydraulic_systems:CG:x", "m") == approx(
        13.48, rel=1e-3
    )

    assert problem.get_val("data:weight:systems:fire_protection:CG:x", "m") == approx(
        12.13, rel=1e-3
    )
    assert problem.get_val("data:weight:systems:automatic_flight_system:CG:x", "m") == approx(
        12.13, rel=1e-3
    )
    assert problem.get_val("data:weight:systems:communications:CG:x", "m") == approx(6.74, rel=1e-3)
    assert problem.get_val("data:weight:systems:ECS:CG:x", "m") == approx(12.22, rel=1e-3)
    assert problem.get_val("data:weight:systems:de-icing:CG:x", "m") == approx(12.286, rel=1e-3)
    assert problem.get_val("data:weight:systems:navigation:CG:x", "m") == approx(3.9887, rel=1e-3)

    assert problem.get_val("data:weight:furniture:furnishing:CG:x", "m") == approx(12.22, rel=1e-3)
    assert problem.get_val("data:weight:furniture:water:CG:x", "m") == approx(21.57, rel=1e-3)
    assert problem.get_val("data:weight:furniture:interior_integration:CG:x", "m") == approx(
        11, rel=1e-3
    )
    assert problem.get_val("data:weight:furniture:insulation:CG:x", "m") == approx(12.13, rel=1e-3)
    assert problem.get_val("data:weight:furniture:cabin_lighting:CG:x", "m") == approx(
        12.13, rel=1e-3
    )
    assert problem.get_val("data:weight:furniture:seats_crew_accommodation:CG:x", "m") == approx(
        12.22, rel=1e-3
    )
    assert problem.get_val("data:weight:furniture:oxygen:CG:x", "m") == approx(12.22, rel=1e-3)

    assert problem.get_val("data:weight:operational:items:documents_toolkit:CG:x", "m") == approx(
        12.22, rel=1e-3
    )
    assert problem.get_val("data:weight:operational:items:galley_structure:CG:x", "m") == approx(
        18.87, rel=1e-3
    )
    assert problem.get_val("data:weight:operational:equipment:others:CG:x", "m") == approx(
        12.17, rel=1e-3
    )
    assert problem.get_val("data:weight:operational:equipment:crew:CG:x", "m") == approx(
        8.089, rel=1e-3
    )
    assert problem.get_val("data:weight:operational:items:unusable_fuel:CG:x", "m") == approx(
        12.88, rel=1e-3
    )

    assert problem.get_val("data:weight:payload:PAX:CG:x", "m") == approx(12.22, rel=1e-3)
    assert problem.get_val("data:weight:payload:rear_fret:CG:x", "m") == approx(14.75, rel=1e-3)
    assert problem.get_val("data:weight:payload:front_fret:CG:x", "m") == approx(8.37, rel=1e-3)


def test_max_cg_ratio():
    ivc = IndepVarComp()
    ivc.add_output(
        "data:weight:aircraft:operating_empty:CG:MAC_position", val=0.0013, units="unitless"
    )
    ivc.add_output("data:weight:aircraft:load_case_1:CG:MAC_position", val=0.0570, units="unitless")
    ivc.add_output("data:weight:aircraft:load_case_2:CG:MAC_position", val=0.025, units="unitless")
    ivc.add_output("data:weight:aircraft:load_case_3:CG:MAC_position", val=0.0362, units="unitless")
    ivc.add_output(
        "settings:weight:aircraft:CG:aft:MAC_position:margin",
        val=0.05,
        units="unitless",
    )

    problem = run_system(ComputeMaxCGratio(), ivc)

    assert problem.get_val(
        "data:weight:aircraft:CG:aft:MAC_position",
    ) == approx(0.107, rel=1e-3)


def test_compute_cg_ratio_aft():
    input_list = [
        "data:weight:airframe:wing:CG:x",
        "data:weight:airframe:fuselage:CG:x",
        "data:weight:airframe:horizontal_tail:CG:x",
        "data:weight:airframe:vertical_tail:CG:x",
        "data:weight:airframe:landing_gear:main:CG:x",
        "data:weight:airframe:landing_gear:front:CG:x",
        "data:weight:airframe:nacelle:CG:x",
        "data:weight:propulsion:engine:CG:x",
        "data:weight:propulsion:propeller:CG:x",
        "data:weight:propulsion:engine_controls_instrumentation:CG:x",
        "data:weight:propulsion:fuel_lines:CG:x",
        "data:weight:systems:auxiliary_power_unit:CG:x",
        "data:weight:systems:electric_systems:electric_generation:CG:x",
        "data:weight:systems:electric_systems:electric_common_installation:CG:x",
        "data:weight:systems:hydraulic_systems:CG:x",
        "data:weight:systems:fire_protection:CG:x",
        "data:weight:systems:flight_furnishing:CG:x",
        "data:weight:systems:automatic_flight_system:CG:x",
        "data:weight:systems:communications:CG:x",
        "data:weight:systems:ECS:CG:x",
        "data:weight:systems:de-icing:CG:x",
        "data:weight:systems:navigation:CG:x",
        "data:weight:systems:flight_controls:CG:x",
        "data:weight:furniture:furnishing:CG:x",
        "data:weight:furniture:water:CG:x",
        "data:weight:furniture:interior_integration:CG:x",
        "data:weight:furniture:insulation:CG:x",
        "data:weight:furniture:cabin_lighting:CG:x",
        "data:weight:furniture:seats_crew_accommodation:CG:x",
        "data:weight:furniture:oxygen:CG:x",
        "data:weight:operational:items:passenger_seats:CG:x",
        "data:weight:operational:items:unusable_fuel:CG:x",
        "data:weight:operational:items:documents_toolkit:CG:x",
        "data:weight:operational:items:galley_structure:CG:x",
        "data:weight:operational:equipment:others:CG:x",
        "data:weight:airframe:wing:mass",
        "data:weight:airframe:fuselage:mass",
        "data:weight:airframe:horizontal_tail:mass",
        "data:weight:airframe:vertical_tail:mass",
        "data:weight:airframe:landing_gear:main:mass",
        "data:weight:airframe:landing_gear:front:mass",
        "data:weight:airframe:nacelle:mass",
        "data:weight:propulsion:engine:mass",
        "data:weight:propulsion:propeller:mass",
        "data:weight:propulsion:engine_controls_instrumentation:mass",
        "data:weight:propulsion:fuel_lines:mass",
        "data:weight:systems:auxiliary_power_unit:mass",
        "data:weight:systems:electric_systems:electric_generation:mass",
        "data:weight:systems:electric_systems:electric_common_installation:mass",
        "data:weight:systems:hydraulic_systems:mass",
        "data:weight:systems:fire_protection:mass",
        "data:weight:systems:flight_furnishing:mass",
        "data:weight:systems:automatic_flight_system:mass",
        "data:weight:systems:communications:mass",
        "data:weight:systems:ECS:mass",
        "data:weight:systems:de-icing:mass",
        "data:weight:systems:navigation:mass",
        "data:weight:systems:flight_controls:mass",
        "data:weight:furniture:furnishing:mass",
        "data:weight:furniture:water:mass",
        "data:weight:furniture:interior_integration:mass",
        "data:weight:furniture:insulation:mass",
        "data:weight:furniture:cabin_lighting:mass",
        "data:weight:furniture:seats_crew_accommodation:mass",
        "data:weight:furniture:oxygen:mass",
        "data:weight:operational:items:passenger_seats:mass",
        "data:weight:operational:items:unusable_fuel:mass",
        "data:weight:operational:items:documents_toolkit:mass",
        "data:weight:operational:items:galley_structure:mass",
        "data:weight:operational:equipment:others:mass",
        "data:weight:operational:equipment:crew:mass",
        "data:weight:operational:equipment:crew:CG:x",
        "data:geometry:wing:MAC:length",
        "data:geometry:wing:MAC:at25percent:x",
    ]

    ivc = get_indep_var_comp(input_list)

    problem = run_system(ComputeCGRatioAft(), ivc)

    assert problem.get_val("data:weight:aircraft_empty:mass", "kg") == approx(13765, abs=1)
    assert problem.get_val("data:weight:aircraft_empty:CG:x", "m") == approx(12.15, rel=1e-3)
    assert problem.get_val("data:weight:aircraft:operating_empty:CG:x", "m") == approx(
        12.06, rel=1e-3
    )
    assert problem.get_val("data:weight:aircraft:operating_empty:mass", "kg") == approx(
        14085, abs=1
    )
