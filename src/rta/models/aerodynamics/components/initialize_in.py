"""
FAST - Copyright (c) 2025 ONERA ISAE
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

from rta.models.aerodynamics.constants import (
    ALPHA_POINT_COUNT,
    CT_POINT_COUNT,
    H_POINT_COUNT,
)

"""
Unknown usage for CT, alpha list and H_list
"""


class InitializeIN(om.ExplicitComponent):
    def setup(self):
        self.add_output("data:aerodynamics:aircraft:low_speed:CT", shape=CT_POINT_COUNT)
        self.add_output(
            "data:aerodynamics:aircraft:low_speed:alpha",
            units="deg",
            shape=ALPHA_POINT_COUNT,
        )
        self.add_output("data:aerodynamics:aircraft:low_speed:H", shape=H_POINT_COUNT, units="m")

    def compute(self, inputs, outputs):
        CT_list = np.linspace(-2, 2.0, CT_POINT_COUNT)
        alpha_list = np.linspace(-1, 12.0, ALPHA_POINT_COUNT)
        H_list = np.linspace(0.0, 30.0, H_POINT_COUNT)

        outputs["data:aerodynamics:aircraft:low_speed:CT"] = CT_list
        outputs["data:aerodynamics:aircraft:low_speed:alpha"] = alpha_list
        outputs["data:aerodynamics:aircraft:low_speed:H"] = H_list
