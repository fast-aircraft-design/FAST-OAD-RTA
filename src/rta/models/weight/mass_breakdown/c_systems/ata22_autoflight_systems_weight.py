"""
Estimation of automatic flight systems weight
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

import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel

from rta.models.weight.mass_breakdown.c_systems.constants import SERVICE_MASS_ATA22


@RegisterSubmodel(SERVICE_MASS_ATA22, "rta.submodel.mass.system.ata22")
class AutoFlightSystemWeight(om.ExplicitComponent):
    """
    Weight estimation for automatic flight systems



    Based on a rough estimation of needed instruments and servo actuators
    """

    def setup(self):
        self.add_input("tuning:weight:systems:automatic_flight_system:mass:k", val=1.0)
        self.add_input(
            "tuning:weight:systems:automatic_flight_system:mass:offset",
            val=0.0,
            units="kg",
        )

        self.add_output("data:weight:systems:automatic_flight_system:mass", units="kg")

        self.declare_partials("*", "*", method="fd")

    # pylint: disable=too-many-locals
    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        k = inputs["tuning:weight:systems:automatic_flight_system:mass:k"]
        offset = inputs["tuning:weight:systems:automatic_flight_system:mass:offset"]

        # Mass of autopilot system
        mass_autopilot = 30
        outputs["data:weight:systems:automatic_flight_system:mass"] = k * mass_autopilot + offset
