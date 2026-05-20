"""
Estimation of environmental control system weight
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

from rta.models.weight.mass_breakdown.c_systems.constants import SERVICE_MASS_ATA21


@RegisterSubmodel(SERVICE_MASS_ATA21, "rta.submodel.mass.system.ata21")
class ECSWeight(ExplicitComponent):
    """
    Weight estimation for environmental control system weight
    This includes:

    - bleed system
    - air conditioning / pressurization
    - air distribution
    - Temperature and pressure control


    Based on "Aircraft conceptual design synthesis", Denis Howe
    Formula (AD4.10b) pag.359
    """

    def setup(self):
        self.add_input("data:geometry:cabin:NPAX1", val=np.nan)
        self.add_input("tuning:weight:systems:ECS:mass:k", val=1.0)
        self.add_input("tuning:weight:systems:ECS:mass:offset", val=0.0, units="kg")

        self.add_output("data:weight:systems:ECS:mass", units="kg")

        self.declare_partials("*", "*", method="fd")

    # pylint: disable=too-many-locals
    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        npax1 = inputs["data:geometry:cabin:NPAX1"]

        k = inputs["tuning:weight:systems:ECS:mass:k"]
        offset = inputs["tuning:weight:systems:ECS:mass:offset"]

        mass_ECS = 4 * npax1 + 60

        # Mass of air conditioning and pressurization system

        outputs["data:weight:systems:ECS:mass"] = k * mass_ECS + offset
