"""
Estimation of life crew accomodation weight
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
from fastoad.module_management.service_registry import RegisterSubmodel

from rta.models.weight.mass_breakdown.d_furniture.constants import SERVICE_MASS_ATA2510


@RegisterSubmodel(SERVICE_MASS_ATA2510, "rta.submodel.mass.furniture.ata2510")
class SeatsCrewWeight(om.ExplicitComponent):
    """
    Weight estimation for crew accomadation

    Based on formulas in :cite:`supaero:2014`, mass contribution C25
    """

    def setup(self):
        self.add_input("data:geometry:cabin:crew_count:technical", val=np.nan, units="unitless")
        self.add_input("data:geometry:cabin:crew_count:commercial", val=np.nan, units="unitless")

        self.add_input(
            "tuning:weight:furniture:seats_crew_accommodation:mass:k", val=1.0, units="unitless"
        )
        self.add_input(
            "tuning:weight:furniture:seats_crew_accommodation:mass:offset",
            val=0.0,
            units="kg",
        )

        self.add_output("data:weight:furniture:seats_crew_accommodation:mass", units="kg")

        self.declare_partials("*", "*", method="fd")

    # pylint: disable=too-many-locals
    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        cabin_crew = inputs["data:geometry:cabin:crew_count:commercial"]
        cockpit_crew = inputs["data:geometry:cabin:crew_count:technical"]

        k = inputs["tuning:weight:furniture:seats_crew_accommodation:mass:k"]
        offset = inputs["tuning:weight:furniture:seats_crew_accommodation:mass:offset"]

        # Mass of seats and installation system
        mass_crew_seats = 20 * cockpit_crew + 10 * cabin_crew
        outputs["data:weight:furniture:seats_crew_accommodation:mass"] = (
            k * mass_crew_seats + offset
        )
