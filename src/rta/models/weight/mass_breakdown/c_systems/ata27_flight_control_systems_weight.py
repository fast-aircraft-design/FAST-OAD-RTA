"""
Estimation of mechanical flight control systems weight
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

from rta.models.weight.mass_breakdown.c_systems.constants import SERVICE_MASS_ATA27


@RegisterSubmodel(SERVICE_MASS_ATA27, "rta.submodel.mass.system.ata27")
class FlightControlsSystemWeight(om.ExplicitComponent):
    """
    Weight estimation for mechanical flight control systems

    This includes:

    - cables
    - pulleys
    - sticks/pedals
    - miscellaneous equipment

    Based on "Aircraft conceptual design synthesis", Denis Howe
    Table (AD4.4) pag.357
    """

    def setup(self):
        self.add_input("data:weight:aircraft:MTOW", val=np.nan, units="kg")

        self.add_input("tuning:weight:systems:flight_controls:mass:k", val=1.0, units="unitless")
        self.add_input("tuning:weight:systems:flight_controls:mass:offset", val=0.0, units="kg")

        self.add_output("data:weight:systems:flight_controls:mass", units="kg")

        self.declare_partials("*", "*", method="fd")

    # pylint: disable=too-many-locals
    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        mtow = inputs["data:weight:aircraft:MTOW"]
        k = inputs["tuning:weight:systems:flight_controls:mass:k"]
        offset = inputs["tuning:weight:systems:flight_controls:mass:offset"]

        # Mass of mechanical flight control system
        mass_fc = 0.01 * mtow
        outputs["data:weight:systems:flight_controls:mass"] = k * mass_fc + offset
