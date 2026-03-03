#  This file is part of FAST-OAD_CS25
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
import os.path as pth

import openmdao.api as om
import pytest
from fastoad.io import VariableIO
from fastoad.testing import run_system

from ..a_airframe.a1_wing_weight import WingWeight
from ..a_airframe.a6_nacelles_weight import NacellesWeight
from ..b_propulsion.turboprop_weight import TurbopropWeight


def get_indep_var_comp(var_names):
    """Reads required input data and returns an IndepVarcomp() instance"""
    reader = VariableIO(pth.join(pth.dirname(__file__), "data", "ref_weight.xml"))
    reader.path_separator = ":"
    ivc = reader.read(only=var_names).to_ivc()
    return ivc


def test_compute_nacelle_weight():
    ivc = om.IndepVarComp()
    ivc.add_output("data:propulsion:RTO_power", val=2.05e6, units="W")
    ivc.add_output("data:geometry:propulsion:engine:count", val=2)
    ivc.add_output("tuning:weight:airframe:nacelle:mass:k", val=1.0)
    ivc.add_output("tuning:weight:airframe:nacelle:mass:offset", val=0.0, units="kg")

    problem = run_system(NacellesWeight(), ivc)

    assert problem.get_val("data:weight:airframe:nacelle:mass", "kg") == pytest.approx(
        349.15, abs=0.1
    )


def test_wing_weight():
    input_list = [
        "data:geometry:wing:root:thickness_ratio",
        "data:geometry:wing:kink:thickness_ratio",
        "data:geometry:wing:tip:thickness_ratio",
        "data:geometry:wing:area",
        "data:geometry:wing:span",
        "data:geometry:wing:root:chord",
        "data:geometry:wing:sweep_25",
        "data:geometry:wing:outer_area",
        "data:weight:aircraft:MTOW",
        "data:mission:sizing:cs25:sizing_load",
        "tuning:weight:airframe:wing:mass:k",
        "tuning:weight:airframe:wing:mass:offset",
        "tuning:weight:airframe:wing:bending_sizing:mass:k",
        "tuning:weight:airframe:wing:bending_sizing:mass:offset",
        "tuning:weight:airframe:wing:shear_sizing:mass:k",
        "tuning:weight:airframe:wing:shear_sizing:mass:offset",
        "tuning:weight:airframe:wing:ribs:mass:k",
        "tuning:weight:airframe:wing:ribs:mass:offset",
        "tuning:weight:airframe:wing:secondary_parts:mass:k",
        "tuning:weight:airframe:wing:secondary_parts:mass:offset",
        "settings:weight:airframe:wing:mass:k_voil",
        "settings:weight:airframe:wing:mass:k_mvo",
    ]

    ivc = get_indep_var_comp(input_list)

    problem = run_system(WingWeight(), ivc)

    assert problem.get_val("data:weight:airframe:wing:mass", "kg") == pytest.approx(2370, abs=1)


def test_turboprop_weight():
    ivc = om.IndepVarComp()
    ivc.add_output("data:propulsion:RTO_power", val=2047252, units="W")
    ivc.add_output("data:geometry:propulsion:engine:count", val=2)
    ivc.add_output("data:geometry:fuselage:length", val=26.962, units="m")
    ivc.add_output("data:geometry:propulsion:propeller:diameter", val=3.926, units="m")
    ivc.add_output("data:geometry:propulsion:propeller:B", val=6)
    ivc.add_output("tuning:weight:propulsion:engine:mass:k", val=1.0)
    ivc.add_output("tuning:weight:propulsion:engine_controls_instrumentation:mass:k", val=1.0)
    ivc.add_output("tuning:weight:propulsion:propeller:mass:k", val=1.0)

    ivc.add_output("data:propulsion:propeller:max_power", val=2239.7, units="kW")

    problem = run_system(TurbopropWeight(), ivc)

    assert problem.get_val("data:weight:propulsion:engine:mass", "kg") == pytest.approx(
        967.84, rel=1e-3
    )
    assert problem.get_val(
        "data:weight:propulsion:engine_controls_instrumentation:mass", "kg"
    ) == pytest.approx(36.73, rel=1e-3)
    assert problem.get_val("data:weight:propulsion:propeller:mass", "kg") == pytest.approx(
        387.21, rel=1e-3
    )
