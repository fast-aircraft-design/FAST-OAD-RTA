"""
Estimation of oxygen systems weight
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

from rta.models.weight.mass_breakdown.d_furniture.constants import SERVICE_MASS_ATA35


@RegisterSubmodel(SERVICE_MASS_ATA35, "rta.submodel.mass.furniture.ata35")
class OxygenWeight(om.ExplicitComponent):
    """
    Weight estimation for oxygen systems



    Based on formulas in :cite:`supaero:2014`, mass contribution C26
    """

    def setup(self):
        self.add_input("data:geometry:cabin:NPAX1", val=np.nan, units="unitless")
        self.add_input("tuning:weight:furniture:oxygen:mass:k", val=1.0, units="unitless")
        self.add_input("tuning:weight:furniture:oxygen:mass:offset", val=0.0, units="kg")

        self.add_output("data:weight:furniture:oxygen:mass", units="kg")

        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        k = inputs["tuning:weight:furniture:oxygen:mass:k"]
        offset = inputs["tuning:weight:furniture:oxygen:mass:offset"]
        npax1 = inputs["data:geometry:cabin:NPAX1"]

        # Mass of fixed oxygen
        mass_oxy = 80 + 1.3 * npax1
        outputs["data:weight:furniture:oxygen:mass"] = k * mass_oxy + offset
