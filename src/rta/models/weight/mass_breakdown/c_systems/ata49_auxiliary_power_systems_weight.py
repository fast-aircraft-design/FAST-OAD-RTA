"""
Estimation of Auxiliary Power Unit (APU) weight
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

from rta.models.weight.mass_breakdown.c_systems.constants import SERVICE_MASS_ATA49


@RegisterSubmodel(SERVICE_MASS_ATA49, "rta.submodel.mass.system.ata49")
class APUWeight(om.ExplicitComponent):
    """
    Weight estimation for Auxiliary Power Unit (APU)


    Based on formulas in :cite:`supaero:2014`, mass contribution C1
    """

    def setup(self):
        self.add_input("data:geometry:cabin:NPAX1", val=np.nan, units="unitless")
        self.add_input(
            "tuning:weight:systems:auxiliary_power_unit:mass:k", val=1.0, units="unitless"
        )
        self.add_input(
            "tuning:weight:systems:auxiliary_power_unit:mass:offset",
            val=0.0,
            units="kg",
        )

        self.add_output("data:weight:systems:auxiliary_power_unit:mass", units="kg")

        self.declare_partials("*", "*", method="fd")

    # pylint: disable=too-many-locals
    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        npax1 = inputs["data:geometry:cabin:NPAX1"]
        k = inputs["tuning:weight:systems:auxiliary_power_unit:mass:k"]
        offset = inputs["tuning:weight:systems:auxiliary_power_unit:mass:offset"]

        # Mass of auxiliary power unit
        mass_apu = 11.3 * npax1**0.64
        outputs["data:weight:systems:auxiliary_power_unit:mass"] = k * mass_apu + offset
