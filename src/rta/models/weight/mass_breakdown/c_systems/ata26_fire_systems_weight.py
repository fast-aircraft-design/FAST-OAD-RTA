"""
Estimation of fire protection weight
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

from rta.models.weight.mass_breakdown.c_systems.constants import SERVICE_MASS_ATA26


@RegisterSubmodel(SERVICE_MASS_ATA26, "rta.submodel.mass.system.ata26")
class FireSystemWeight(om.ExplicitComponent):
    """
    Weight estimation for fire protection systems

    This includes:

    - Fire detection
    - Fire extinguish

    Based on rough estimation of needed components mass
    """

    def setup(self):
        self.add_input("tuning:weight:systems:fire_protection:mass:k", val=1.0)
        self.add_input("tuning:weight:systems:fire_protection:mass:offset", val=0.0, units="kg")

        self.add_output("data:weight:systems:fire_protection:mass", units="kg")

        self.declare_partials("*", "*", method="fd")

    # pylint: disable=too-many-locals
    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        k = inputs["tuning:weight:systems:fire_protection:mass:k"]
        offset = inputs["tuning:weight:systems:fire_protection:mass:offset"]

        # Mass of fire protection system
        mass_fire = 25
        outputs["data:weight:systems:fire_protection:mass"] = k * mass_fire + offset
