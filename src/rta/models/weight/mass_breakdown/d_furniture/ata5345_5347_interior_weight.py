"""
Estimation of interior fuselage support systems weight
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

from rta.models.weight.mass_breakdown.d_furniture.constants import SERVICE_MASS_ATA5345


@RegisterSubmodel(SERVICE_MASS_ATA5345, "rta.submodel.mass.furniture.ata5347")
class InteriorIntegrationWeight(om.ExplicitComponent):
    """
    Weight estimation for interior fuselage supports

    This includes:

    - Fuselage, Seat/Cargo Attach Fittings
    - Fuselage, Equipment Attach Fittings
    - Fuselage, Door Hinge

    Based on a rough estimation percentage of MTOW

    """

    def setup(self):
        self.add_input("data:weight:aircraft:MTOW", val=np.nan, units="kg")

        self.add_input("tuning:weight:furniture:interior_integration:mass:k", val=1.0)
        self.add_input(
            "tuning:weight:furniture:interior_integration:mass:offset",
            val=0.0,
            units="kg",
        )

        self.add_output("data:weight:furniture:interior_integration:mass", units="kg")

        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        mtow = inputs["data:weight:aircraft:MTOW"]
        k = inputs["tuning:weight:furniture:interior_integration:mass:k"]
        offset = inputs["tuning:weight:furniture:interior_integration:mass:offset"]

        mass_furn = 0.005 * mtow

        outputs["data:weight:furniture:interior_integration:mass"] = k * mass_furn + offset
