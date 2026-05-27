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

from ..ata25_furnishing_weight import FurnishingWeight
from ..ata33_lighting_weight import LightsWeight
from ..ata35_oxygen_weight import OxygenWeight
from ..ata38_water_weight import WaterWeight
from ..ata2510_crew_seats_weight import SeatsCrewWeight
from ..ata2580_insulation_weight import InsulationWeight
from ..ata5345_5347_interior_weight import InteriorIntegrationWeight


def get_indep_var_comp(var_names):
    """Reads required input data and returns an IndepVarcomp() instance"""
    reader = VariableIO(Path(__file__).parent.resolve() / "data" / "ref_weight.xml")
    reader.path_separator = ":"
    return reader.read(only=var_names).to_ivc()


def test_water_weight():
    ivc = IndepVarComp()
    ivc.add_output("tuning:weight:furniture:water:mass:k", val=1.0)
    ivc.add_output("tuning:weight:furniture:water:mass:offset", val=0.0, units="kg")

    problem = run_system(WaterWeight(), ivc)

    assert problem.get_val("data:weight:furniture:water:mass", "kg") == approx(10, abs=0.1)


def test_furnishing_weight():
    ivc = IndepVarComp()
    ivc.add_output("data:weight:aircraft:MTOW", val=23e3, units="kg")

    ivc.add_output("tuning:weight:furniture:furnishing:mass:k", val=1.0)
    ivc.add_output("tuning:weight:furniture:furnishing:mass:offset", val=0.0, units="kg")

    problem = run_system(FurnishingWeight(), ivc)

    assert problem.get_val("data:weight:furniture:furnishing:mass", "kg") == approx(920, abs=1)


def test_oxygen_weight():
    ivc = IndepVarComp()
    ivc.add_output("data:geometry:cabin:NPAX1", val=75)
    ivc.add_output("tuning:weight:furniture:oxygen:mass:k", val=1.0)
    ivc.add_output("tuning:weight:furniture:oxygen:mass:offset", val=0.0, units="kg")

    problem = run_system(OxygenWeight(), ivc)

    assert problem.get_val("data:weight:furniture:oxygen:mass", "kg") == approx(177.5, abs=0.5)


def test_light_weight():
    ivc = IndepVarComp()
    ivc.add_output("data:geometry:fuselage:maximum_width", val=2.79, units="m")
    ivc.add_output("data:geometry:fuselage:maximum_height", val=2.933, units="m")
    ivc.add_output("data:geometry:cabin:length", val=21.839, units="m")
    ivc.add_output("tuning:weight:furniture:cabin_lighting:mass:k", val=1.0)
    ivc.add_output("tuning:weight:furniture:cabin_lighting:mass:offset", val=0.0, units="kg")

    problem = run_system(LightsWeight(), ivc)

    assert problem.get_val("data:weight:furniture:cabin_lighting:mass", "kg") == approx(
        87.46, abs=0.1
    )


def test_insulation_weight():
    ivc = IndepVarComp()
    ivc.add_output("data:geometry:fuselage:maximum_width", val=2.79, units="m")
    ivc.add_output("data:geometry:fuselage:maximum_height", val=2.933, units="m")
    ivc.add_output("data:geometry:cabin:length", val=21.839, units="m")
    ivc.add_output("tuning:weight:furniture:insulation:mass:k", val=1.0)
    ivc.add_output("tuning:weight:furniture:insulation:mass:offset", val=0.0, units="kg")

    problem = run_system(InsulationWeight(), ivc)

    assert problem.get_val("data:weight:furniture:insulation:mass", "kg") == approx(581, abs=1)


def test_crew_seat_weight():
    ivc = IndepVarComp()
    ivc.add_output("data:geometry:cabin:crew_count:technical", val=2.0)
    ivc.add_output("data:geometry:cabin:crew_count:commercial", val=2.0)

    ivc.add_output("tuning:weight:furniture:seats_crew_accommodation:mass:k", val=1.0)
    ivc.add_output(
        "tuning:weight:furniture:seats_crew_accommodation:mass:offset",
        val=0.0,
        units="kg",
    )

    problem = run_system(SeatsCrewWeight(), ivc)

    assert problem.get_val("data:weight:furniture:seats_crew_accommodation:mass", "kg") == approx(
        60, abs=0.1
    )


def test_interior_weight():
    ivc = IndepVarComp()
    ivc.add_output("data:weight:aircraft:MTOW", val=23e3, units="kg")
    ivc.add_output("tuning:weight:furniture:interior_integration:mass:k", val=1.0)
    ivc.add_output(
        "tuning:weight:furniture:interior_integration:mass:offset",
        val=0.0,
        units="kg",
    )

    problem = run_system(InteriorIntegrationWeight(), ivc)

    assert problem.get_val("data:weight:furniture:interior_integration:mass", "kg") == approx(
        115, abs=0.1
    )
