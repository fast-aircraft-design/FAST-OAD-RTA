"""
Estimation of passenger seats weight
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

from rta.models.weight.mass_breakdown.d_furniture.constants import (
    SERVICE_MASS_ATA25_FURNISHING,
)


@RegisterSubmodel(SERVICE_MASS_ATA25_FURNISHING, "rta.submodel.mass.furniture.ata25")
class FurnishingWeight(om.ExplicitComponent):
    """
    Weight estimation for furnishing weight. It includes:

        - Toilets
        - Cargo equipments
        - Baggage racks
        - Trimming panels
        - Doors/curtains

    Based on "Aircraft conceptual design synthesis", Denis Howe
    Table (AD4.4) pag.357
    """

    def setup(self):
        self.add_input("data:weight:aircraft:MTOW", val=np.nan, units="kg")

        self.add_input("tuning:weight:furniture:furnishing:mass:k", val=1.0)
        self.add_input("tuning:weight:furniture:furnishing:mass:offset", val=0.0, units="kg")

        self.add_output("data:weight:furniture:furnishing:mass", units="kg")

        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        mtow = inputs["data:weight:aircraft:MTOW"]
        k = inputs["tuning:weight:furniture:furnishing:mass:k"]
        offset = inputs["tuning:weight:furniture:furnishing:mass:offset"]

        mass_furn = 0.04 * mtow

        outputs["data:weight:furniture:furnishing:mass"] = k * mass_furn + offset
