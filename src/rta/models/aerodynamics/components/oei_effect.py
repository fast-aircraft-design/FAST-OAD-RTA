"""
Computation of Oswald coefficient
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
from scipy import constants

from rta.models.aerodynamics.constants import CT_POINT_COUNT


class ComputeDeltaOEI(om.ExplicitComponent):
    """
    Computes One engine inoperative effect on Cd. Based on Raymer page 290 eq 12.40
    Trim effects calculation is not referenced
    """

    def initialize(self):
        self.options.declare("landing_flag", default=False, types=bool)

    def setup(self):
        self.add_input("data:geometry:propulsion:nacelle:y", val=np.nan, units="m")
        self.add_input("data:geometry:propulsion:propeller:B", val=np.nan)
        self.add_input("data:geometry:propulsion:propeller:diameter", val=np.nan, units="m")
        self.add_input("data:geometry:vertical_tail:aspect_ratio", val=np.nan)
        self.add_input("data:geometry:wing:area", val=np.nan, units="m**2")
        self.add_input("data:geometry:vertical_tail:area", val=np.nan, units="m**2")
        self.add_input(
            "data:geometry:vertical_tail:MAC:at25percent:x:from_wingMAC25",
            val=np.nan,
            units="m",
        )

        self.add_input("data:aerodynamics:aircraft:low_speed:CT", shape=CT_POINT_COUNT)
        self.add_input("data:aerodynamics:aircraft:low_speed:DCD_ext", val=0.0)

        self.add_output("data:aerodynamics:aircraft:low_speed:DCD_feather", val=0.004)
        self.add_output(
            "data:aerodynamics:aircraft:landing:OEI_effect:DCD",
            copy_shape="data:aerodynamics:aircraft:low_speed:CT",
        )
        self.add_output(
            "data:aerodynamics:aircraft:takeoff:OEI_effect:DCD",
            copy_shape="data:aerodynamics:aircraft:low_speed:CT",
        )
        self.add_output(
            "data:aerodynamics:aircraft:low_speed:OEI_effect:DCD",
            copy_shape="data:aerodynamics:aircraft:low_speed:CT",
        )
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs):
        n_blades = inputs["data:geometry:propulsion:propeller:B"]
        d_prop = inputs["data:geometry:propulsion:propeller:diameter"]
        dCd_ext = inputs["data:aerodynamics:aircraft:low_speed:DCD_ext"]
        CT_list = inputs["data:aerodynamics:aircraft:low_speed:CT"]
        y_nacelle = inputs["data:geometry:propulsion:nacelle:y"]
        lambda_vt = inputs["data:geometry:vertical_tail:aspect_ratio"]
        wing_area = inputs["data:geometry:wing:area"]
        vt_area = inputs["data:geometry:vertical_tail:area"]
        lp_vt = inputs["data:geometry:vertical_tail:MAC:at25percent:x:from_wingMAC25"]
        dCd_feather = (
            1.0
            / (wing_area / constants.foot**2)
            * (0.1 * n_blades / (8 * np.pi) * (np.pi * (d_prop / 2.0 / constants.foot) ** 2))
        )

        DCD_trim_list = []
        for CT in CT_list:
            dCd_trim = (
                1.75
                / (np.pi * lambda_vt)
                * y_nacelle**2
                * wing_area
                / (lp_vt**2 * vt_area)
                * (CT + dCd_feather) ** 2
            )
            DCD_trim_list.append(dCd_trim)

        dCd_OEI = np.array(DCD_trim_list) + dCd_feather + dCd_ext

        outputs["data:aerodynamics:aircraft:low_speed:DCD_feather"] = dCd_feather
        outputs["data:aerodynamics:aircraft:landing:OEI_effect:DCD"] = dCd_OEI
        outputs["data:aerodynamics:aircraft:takeoff:OEI_effect:DCD"] = dCd_OEI
        outputs["data:aerodynamics:aircraft:low_speed:OEI_effect:DCD"] = dCd_OEI
