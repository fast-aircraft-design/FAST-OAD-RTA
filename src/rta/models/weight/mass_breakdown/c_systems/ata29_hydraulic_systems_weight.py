"""
Estimation of hydraulic power systems weight
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
from fastoad.module_management.service_registry import RegisterSubmodel
from openmdao.core.explicitcomponent import ExplicitComponent

from rta.models.weight.mass_breakdown.c_systems.constants import SERVICE_MASS_ATA29


@RegisterSubmodel(SERVICE_MASS_ATA29, "rta.submodel.mass.system.ata29")
class HydraulicPowerSystemWeight(ExplicitComponent):
    """
    Weight estimation for hydraulic power systems (generation and distribution)

    This includes:

    - hydraulic reservoir
    - hydraulic fluid
    - pumps
    - tubing
    - valves
    - installation supports

    Based on "Aircraft conceptual design synthesis", Denis Howe
    Table (AD4.4) pag.357
    """

    def setup(self):
        self.add_input("data:weight:aircraft:MTOW", val=np.nan, units="kg")

        self.add_input("tuning:weight:systems:hydraulic_systems:mass:k", val=1.0)
        self.add_input("tuning:weight:systems:hydraulic_systems:mass:offset", val=0.0, units="kg")

        self.add_output("data:weight:systems:hydraulic_systems:mass", units="kg")

        self.declare_partials("*", "*", method="fd")

    # pylint: disable=too-many-locals
    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        mtow = inputs["data:weight:aircraft:MTOW"]
        k = inputs["tuning:weight:systems:hydraulic_systems:mass:k"]
        offset = inputs["tuning:weight:systems:hydraulic_systems:mass:offset"]

        # Mass of hydraulic power system
        mass_hyd = 0.008 * mtow
        outputs["data:weight:systems:hydraulic_systems:mass"] = k * mass_hyd + offset
