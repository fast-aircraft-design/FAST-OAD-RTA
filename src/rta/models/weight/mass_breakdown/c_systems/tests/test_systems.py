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
from pathlib import Path

from fastoad.io import VariableIO
from fastoad.testing import run_system
from openmdao.api import IndepVarComp
from pytest import approx

from ..ata21_environmental_control_systems_weight import ECSWeight
from ..ata22_autoflight_systems_weight import AutoFlightSystemWeight
from ..ata23_communication_systems_weight import CommunicationSystemWeightLegacy
from ..ata24_electrical_systems_weight import ElectricalPowerSystemWeight
from ..ata25_flight_furnishing_systems_weight import FlightFurnishingWeight
from ..ata26_fire_systems_weight import FireSystemWeight
from ..ata27_flight_control_systems_weight import FlightControlsSystemWeight
from ..ata29_hydraulic_systems_weight import HydraulicPowerSystemWeight
from ..ata30_de_ice_systems_weight import DeIceSystemWeight
from ..ata34_navigation_systems_weight import NavigationSystemWeight
from ..ata49_auxiliary_power_systems_weight import APUWeight


def get_indep_var_comp(var_names):
    """Reads required input data and returns an IndepVarcomp() instance"""
    reader = VariableIO(Path(__file__).parent.resolve() / "data" / "ref_weight.xml")
    reader.path_separator = ":"
    return reader.read(only=var_names).to_ivc()


def test_ecs_weight():
    ivc = IndepVarComp()
    ivc.add_output("data:geometry:cabin:NPAX1", val=75)
    ivc.add_output("tuning:weight:systems:ECS:mass:k", val=1.0)
    ivc.add_output("tuning:weight:systems:ECS:mass:offset", val=0.0, units="kg")

    problem = run_system(ECSWeight(), ivc)

    assert problem.get_val("data:weight:systems:ECS:mass", "kg") == approx(360, abs=1)


def test_autoflight_weight():
    ivc = IndepVarComp()
    ivc.add_output("tuning:weight:systems:automatic_flight_system:mass:k", val=1.0)
    ivc.add_output(
        "tuning:weight:systems:automatic_flight_system:mass:offset",
        val=0.0,
        units="kg",
    )

    problem = run_system(AutoFlightSystemWeight(), ivc)

    assert problem.get_val("data:weight:systems:automatic_flight_system:mass", "kg") == approx(
        30, abs=0.1
    )


def test_communication_system_from_cs25():
    ivc = IndepVarComp()

    ivc.add_output("data:TLAR:range", val=750, units="NM")
    ivc.add_output("tuning:weight:systems:communications:mass:k", val=0.8)
    ivc.add_output("tuning:weight:systems:communications:mass:offset", val=1.0, units="kg")

    problem = run_system(CommunicationSystemWeightLegacy(), ivc)

    assert problem.get_val("data:weight:systems:communications:mass", "kg") == approx(81, abs=0.1)


def test_electric_system_weight():
    ivc = IndepVarComp()
    ivc.add_output("data:geometry:cabin:NPAX1", val=75)
    ivc.add_output("data:weight:aircraft:MTOW", val=23e3, units="kg")
    ivc.add_output(
        "tuning:weight:systems:electric_systems:electric_generation:mass:offset",
        val=0.0,
        units="kg",
    )
    ivc.add_output(
        "tuning:weight:systems:electric_systems:electric_generation:mass:k",
        val=1.0,
        units="unitless",
    )
    ivc.add_output(
        "settings:weight:systems:electric_systems:mass:k_elec", val=1.0, units="unitless"
    )

    problem = run_system(ElectricalPowerSystemWeight(), ivc)

    assert problem.get_val(
        "data:weight:systems:electric_systems:electric_generation:mass", "kg"
    ) == approx(315.8, abs=0.1)
    assert problem.get_val(
        "data:weight:systems:electric_systems:electric_common_installation:mass", "kg"
    ) == approx(210.5, abs=0.1)


def test_flight_furnishing_weight():
    ivc = IndepVarComp()
    ivc.add_output("tuning:weight:systems:flight_furnishing:mass:k", val=1.0)
    ivc.add_output("tuning:weight:systems:flight_furnishing:mass:offset", val=0.0, units="kg")

    problem = run_system(FlightFurnishingWeight(), ivc)

    assert problem.get_val("data:weight:systems:flight_furnishing:mass", "kg") == approx(
        100, abs=0.1
    )


def test_fire_system_weight():
    ivc = IndepVarComp()
    ivc.add_output("tuning:weight:systems:fire_protection:mass:k", val=1.0)
    ivc.add_output("tuning:weight:systems:fire_protection:mass:offset", val=0.0, units="kg")

    problem = run_system(FireSystemWeight(), ivc)

    assert problem.get_val("data:weight:systems:fire_protection:mass", "kg") == approx(25, abs=0.1)


def test_flight_control_weight():
    ivc = IndepVarComp()
    ivc.add_output("data:weight:aircraft:MTOW", val=23e3, units="kg")
    ivc.add_output("tuning:weight:systems:flight_controls:mass:k", val=1.0)
    ivc.add_output("tuning:weight:systems:flight_controls:mass:offset", val=0.0, units="kg")

    problem = run_system(FlightControlsSystemWeight(), ivc)

    assert problem.get_val("data:weight:systems:flight_controls:mass", "kg") == approx(230, abs=0.5)


def test_hydraulic_weight():
    ivc = IndepVarComp()
    ivc.add_output("data:weight:aircraft:MTOW", val=23e3, units="kg")
    ivc.add_output("tuning:weight:systems:hydraulic_systems:mass:k", val=1.0)
    ivc.add_output("tuning:weight:systems:hydraulic_systems:mass:offset", val=0.0, units="kg")

    problem = run_system(HydraulicPowerSystemWeight(), ivc)

    assert problem.get_val("data:weight:systems:hydraulic_systems:mass", "kg") == approx(
        184, abs=0.1
    )


def test_de_ice_weight():
    ivc = IndepVarComp()
    ivc.add_output("data:geometry:fuselage:maximum_width", val=2.78, units="m")
    ivc.add_output("data:geometry:wing:sweep_0", val=3.5, units="deg")
    ivc.add_output("data:geometry:wing:span", val=26.8, units="m")
    ivc.add_output("data:geometry:horizontal_tail:sweep_0", val=9.3, units="deg")
    ivc.add_output("data:geometry:horizontal_tail:span", val=6.1, units="m")
    ivc.add_output("tuning:weight:systems:de-icing:mass:k", val=1.0)
    ivc.add_output("tuning:weight:systems:de-icing:mass:offset", val=0.0, units="kg")

    problem = run_system(DeIceSystemWeight(), ivc)

    assert problem.get_val("data:weight:systems:de-icing:mass", "kg") == approx(110.5, abs=0.1)


def test_navigation_system_weight():
    ivc = IndepVarComp()
    ivc.add_output("data:geometry:fuselage:length", val=27, units="m")
    ivc.add_output("data:geometry:wing:b_50", val=26.8, units="m")
    ivc.add_output("tuning:weight:systems:navigation:mass:k", val=1.0)
    ivc.add_output("tuning:weight:systems:navigation:mass:offset", val=0.0, units="kg")

    problem = run_system(NavigationSystemWeight(), ivc)

    assert problem.get_val("data:weight:systems:navigation:mass", "kg") == approx(173.9, abs=0.1)


def test_APU_weight():
    ivc = IndepVarComp()
    ivc.add_output("data:geometry:cabin:NPAX1", val=75)
    ivc.add_output("tuning:weight:systems:auxiliary_power_unit:mass:k", val=1.0)
    ivc.add_output(
        "tuning:weight:systems:auxiliary_power_unit:mass:offset",
        val=0.0,
        units="kg",
    )

    problem = run_system(APUWeight(), ivc)

    assert problem.get_val("data:weight:systems:auxiliary_power_unit:mass", "kg") == approx(
        179.1, abs=0.1
    )
