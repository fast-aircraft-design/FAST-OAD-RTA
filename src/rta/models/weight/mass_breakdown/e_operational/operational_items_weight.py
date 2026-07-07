"""
Estimation of operational items weight
"""
#  This file is part of FAST : A framework for rapid Overall Aircraft Design
#  Copyright (C) 2020  ONERA & ISAE-SUPAERO
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

import numpy as np
import openmdao.api as om


class OperationalItemsWeight(om.ExplicitComponent):
    """
    Weight estimation for operational items. It includes:
        - Unusable fuel
        - Tool kit and documents
        - Galley
        - Passenger seats
    """

    def setup(self):
        self.add_input("data:TLAR:NPAX", val=np.nan, units="unitless")
        self.add_input("settings:weight:aircraft:design_mass_per_seat", val=np.nan, units="kg")
        self.add_input("tuning:weight:furniture:passenger_seats:mass:k", val=1.0, units="unitless")
        self.add_input("tuning:weight:furniture:passenger_seats:mass:offset", val=0.0, units="kg")

        self.add_output("data:weight:operational:items:passenger_seats:mass", units="kg")
        self.add_output("data:weight:operational:items:unusable_fuel:mass", units="kg")
        self.add_output("data:weight:operational:items:documents_toolkit:mass", units="kg")
        self.add_output("data:weight:operational:items:galley_structure:mass", units="kg")

        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        npax = inputs["data:TLAR:NPAX"]

        k = inputs["tuning:weight:furniture:passenger_seats:mass:k"]
        offset = inputs["tuning:weight:furniture:passenger_seats:mass:offset"]

        mass_per_seat = inputs["settings:weight:aircraft:design_mass_per_seat"]

        outputs["data:weight:operational:items:passenger_seats:mass"] = (
            mass_per_seat * npax * k + offset
        )
        outputs["data:weight:operational:items:unusable_fuel:mass"] = 30.0
        outputs["data:weight:operational:items:documents_toolkit:mass"] = 15.0
        outputs["data:weight:operational:items:galley_structure:mass"] = 100.0
