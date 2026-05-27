"""
Estimation of lighting systems weight
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

from rta.models.weight.mass_breakdown.d_furniture.constants import SERVICE_MASS_ATA33


@RegisterSubmodel(SERVICE_MASS_ATA33, "rta.submodel.mass.furniture.ata33")
class LightsWeight(om.ExplicitComponent):
    """
    Weight estimation for lighting systems


    Based on formulas in :cite:`supaero:2014`, mass contribution C24
    """

    def setup(self):
        self.add_input("data:geometry:fuselage:maximum_width", val=np.nan, units="m")
        self.add_input("data:geometry:fuselage:maximum_height", val=np.nan, units="m")
        self.add_input("data:geometry:cabin:length", val=np.nan, units="m")

        self.add_input("tuning:weight:furniture:cabin_lighting:mass:k", val=1.0)
        self.add_input("tuning:weight:furniture:cabin_lighting:mass:offset", val=0.0, units="kg")

        self.add_output("data:weight:furniture:cabin_lighting:mass", units="kg")

        self.declare_partials("*", "*", method="fd")

    # pylint: disable=too-many-locals
    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        width_max = inputs["data:geometry:fuselage:maximum_width"]
        height_max = inputs["data:geometry:fuselage:maximum_height"]
        cabin_length = inputs["data:geometry:cabin:length"]

        k_c24 = inputs["tuning:weight:furniture:cabin_lighting:mass:k"]
        offset_c24 = inputs["tuning:weight:furniture:cabin_lighting:mass:offset"]

        fuselage_diameter = np.sqrt(width_max * height_max)

        # Mass of internal lighting system
        temp_c24 = 1.4 * cabin_length * fuselage_diameter
        outputs["data:weight:furniture:cabin_lighting:mass"] = k_c24 * temp_c24 + offset_c24
