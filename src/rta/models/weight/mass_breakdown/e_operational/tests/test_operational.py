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

from fastoad.testing import run_system
from openmdao.api import IndepVarComp
from pytest import approx

from ..operational_equipment_weight import OperationalEquipmentsWeight
from ..operational_items_weight import OperationalItemsWeight


def test_items_weight():
    ivc = IndepVarComp()
    ivc.add_output("data:TLAR:NPAX", val=72)
    ivc.add_output("settings:weight:aircraft:design_mass_per_seat", val=10, units="kg")
    ivc.add_output("tuning:weight:furniture:passenger_seats:mass:k", val=1.0)
    ivc.add_output("tuning:weight:furniture:passenger_seats:mass:offset", val=0.0, units="kg")

    problem = run_system(OperationalItemsWeight(), ivc)

    assert problem.get_val("data:weight:operational:items:passenger_seats:mass", "kg") == approx(
        720, abs=0.1
    )
    assert problem.get_val("data:weight:operational:items:unusable_fuel:mass", "kg") == approx(
        30, abs=0.1
    )
    assert problem.get_val("data:weight:operational:items:documents_toolkit:mass", "kg") == approx(
        15, abs=0.1
    )
    assert problem.get_val("data:weight:operational:items:galley_structure:mass", "kg") == approx(
        100, abs=0.1
    )


def test_equipment_weight():
    ivc = IndepVarComp()
    ivc.add_output("data:geometry:cabin:crew_count:technical", val=2.0, units="unitless")
    ivc.add_output("data:geometry:cabin:crew_count:commercial", val=2.0)

    problem = run_system(OperationalEquipmentsWeight(), ivc)

    assert problem.get_val("data:weight:operational:equipment:crew:mass", "kg") == approx(
        320, abs=0.1
    )
    assert problem.get_val("data:weight:operational:equipment:others:mass", "kg") == approx(
        100, abs=0.1
    )
