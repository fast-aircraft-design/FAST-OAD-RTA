"""
Estimation of flight furnishing systems weight
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

from fastoad.module_management.service_registry import RegisterSubmodel
from openmdao.core.explicitcomponent import ExplicitComponent

from rta.models.weight.mass_breakdown.c_systems.constants import (
    SERVICE_MASS_ATA25_SYSTEM,
)


@RegisterSubmodel(SERVICE_MASS_ATA25_SYSTEM, "rta.submodel.mass.system.ata25")
class FlightFurnishingWeight(ExplicitComponent):
    """
    Weight estimation for flight compartment furnishing

    This includes:

    - flight deck structure
    - flight deck panels
    - flight deck miscellaneous equipment

    Based on rough estimation of needed components mass
    """

    def setup(self):
        self.add_input("tuning:weight:systems:flight_furnishing:mass:k", val=1.0)
        self.add_input("tuning:weight:systems:flight_furnishing:mass:offset", val=0.0, units="kg")

        self.add_output("data:weight:systems:flight_furnishing:mass", units="kg")

        self.declare_partials("*", "*", method="fd")

    # pylint: disable=too-many-locals
    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        k = inputs["tuning:weight:systems:flight_furnishing:mass:k"]
        offset = inputs["tuning:weight:systems:flight_furnishing:mass:offset"]

        # Mass of flight furnishing system
        mass_furn = 100
        outputs["data:weight:systems:flight_furnishing:mass"] = k * mass_furn + offset
