"""
Estimation of  thermo-acoustic insulation systems weight
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

from rta.models.weight.mass_breakdown.d_furniture.constants import SERVICE_MASS_ATA2580


@RegisterSubmodel(SERVICE_MASS_ATA2580, "rta.submodel.mass.furniture.ata2580")
class InsulationWeight(om.ExplicitComponent):
    """
    Weight estimation for thermo-acoustic insulation systems



    Based on formulas in :cite:`supaero:2014`, mass contribution C21
    """

    def setup(self):
        self.add_input("data:geometry:fuselage:maximum_width", val=np.nan, units="m")
        self.add_input("data:geometry:fuselage:maximum_height", val=np.nan, units="m")
        self.add_input("data:geometry:cabin:length", val=np.nan, units="m")

        self.add_input("tuning:weight:furniture:insulation:mass:k", val=1.0)
        self.add_input("tuning:weight:furniture:insulation:mass:offset", val=0.0, units="kg")

        self.add_output("data:weight:furniture:insulation:mass", units="kg")

        self.declare_partials("*", "*", method="fd")

    # pylint: disable=too-many-locals
    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        width_max = inputs["data:geometry:fuselage:maximum_width"]
        height_max = inputs["data:geometry:fuselage:maximum_height"]
        cabin_length = inputs["data:geometry:cabin:length"]

        k = inputs["tuning:weight:furniture:insulation:mass:k"]
        offset = inputs["tuning:weight:furniture:insulation:mass:offset"]

        fuselage_diameter = np.sqrt(width_max * height_max)

        # Mass of insulating system
        m_ins = 9.3 * fuselage_diameter * cabin_length
        outputs["data:weight:furniture:insulation:mass"] = k * m_ins + offset
