"""
Estimation of wing center of gravity
"""
#  This file is part of FAST-OAD_CS25
#  Copyright (C) 2026 ONERA & ISAE-SUPAERO
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

import fastoad.api as oad
import numpy as np
import openmdao.api as om
from fastoad_cs25.models.weight.cg.constants import SERVICE_WING_CG

oad.RegisterSubmodel.active_models[SERVICE_WING_CG] = "rta.submodel.weight.cg.wing.legacy"

LIMIT_WING_BREAK = 0.35


@oad.RegisterSubmodel(SERVICE_WING_CG, "rta.submodel.weight.cg.wing.legacy")
class ComputeWingCG(om.ExplicitComponent):
    # Based on FAST-OAD-CS25 Adapted to high wing and specific variable name of wing dihedral
    # TODO: consider including high wing option within FAST-OAD-CS25 and harmonizing dihedral
    #  variable name.
    """Wing center of gravity estimation"""

    def setup(self):
        self.add_input("data:geometry:wing:kink:span_ratio", val=np.nan, units="unitless")
        self.add_input("data:geometry:wing:spar_ratio:front:root", val=np.nan, units="unitless")
        self.add_input("data:geometry:wing:spar_ratio:front:kink", val=np.nan, units="unitless")
        self.add_input("data:geometry:wing:spar_ratio:front:tip", val=np.nan, units="unitless")
        self.add_input("data:geometry:wing:spar_ratio:rear:root", val=np.nan, units="unitless")
        self.add_input("data:geometry:wing:spar_ratio:rear:kink", val=np.nan, units="unitless")
        self.add_input("data:geometry:wing:spar_ratio:rear:tip", val=np.nan, units="unitless")
        self.add_input("data:geometry:wing:span", val=np.nan, units="m")
        self.add_input("data:geometry:wing:root:dihedral", val=np.nan, units="rad")
        self.add_input("data:geometry:wing:MAC:leading_edge:x:local", val=np.nan, units="m")
        self.add_input("data:geometry:wing:root:chord", val=np.nan, units="m")
        self.add_input("data:geometry:wing:kink:chord", val=np.nan, units="m")
        self.add_input("data:geometry:wing:tip:chord", val=np.nan, units="m")
        self.add_input("data:geometry:wing:root:y", val=np.nan, units="m")
        self.add_input("data:geometry:wing:root:thickness_ratio", val=np.nan, units="unitless")
        self.add_input("data:geometry:wing:kink:leading_edge:x:local", val=np.nan, units="m")
        self.add_input("data:geometry:wing:kink:y", val=np.nan, units="m")
        self.add_input("data:geometry:wing:kink:thickness_ratio", val=np.nan, units="unitless")
        self.add_input("data:geometry:wing:tip:leading_edge:x:local", val=np.nan, units="m")
        self.add_input("data:geometry:wing:tip:y", val=np.nan, units="m")
        self.add_input("data:geometry:wing:tip:thickness_ratio", val=np.nan, units="unitless")
        self.add_input("data:geometry:wing:MAC:at25percent:x", val=np.nan, units="m")
        self.add_input("data:geometry:fuselage:maximum_height", val=np.nan, units="m")

        self.add_output("data:weight:airframe:wing:CG:x", units="m")
        self.add_output("data:weight:airframe:wing:CG:z", units="m")
        self.add_output("data:weight:airframe:wing:CG:thickness", units="m")

    def setup_partials(self):
        self.declare_partials("data:weight:airframe:wing:CG:x", "*", method="fd")
        self.declare_partials("data:weight:airframe:wing:CG:z", "*", method="fd")
        self.declare_partials("data:weight:airframe:wing:CG:thickness", "*", method="fd")

    def compute(self, inputs, outputs):
        wing_break = inputs["data:geometry:wing:kink:span_ratio"]
        front_spar_ratio_root = inputs["data:geometry:wing:spar_ratio:front:root"]
        front_spar_ratio_middle = inputs["data:geometry:wing:spar_ratio:front:kink"]
        front_spar_ratio_tip = inputs["data:geometry:wing:spar_ratio:front:tip"]
        rear_spar_ratio_root = inputs["data:geometry:wing:spar_ratio:rear:root"]
        rear_spar_ratio_middle = inputs["data:geometry:wing:spar_ratio:rear:kink"]
        rear_spar_ratio_tip = inputs["data:geometry:wing:spar_ratio:rear:tip"]
        span = inputs["data:geometry:wing:span"]
        dihedral = inputs["data:geometry:wing:root:dihedral"]
        x0_wing = inputs["data:geometry:wing:MAC:leading_edge:x:local"]
        l2_wing = inputs["data:geometry:wing:root:chord"]
        l3_wing = inputs["data:geometry:wing:kink:chord"]
        l4_wing = inputs["data:geometry:wing:tip:chord"]
        y2_wing = inputs["data:geometry:wing:root:y"]
        root_thickness_ratio = inputs["data:geometry:wing:root:thickness_ratio"]
        x3_wing = inputs["data:geometry:wing:kink:leading_edge:x:local"]
        y3_wing = inputs["data:geometry:wing:kink:y"]
        kink_thickness_ratio = inputs["data:geometry:wing:kink:thickness_ratio"]
        y4_wing = inputs["data:geometry:wing:tip:y"]
        x4_wing = inputs["data:geometry:wing:tip:leading_edge:x:local"]
        tip_thickness_ratio = inputs["data:geometry:wing:tip:thickness_ratio"]
        fa_length = inputs["data:geometry:wing:MAC:at25percent:x"]
        height_max = inputs["data:geometry:fuselage:maximum_height"]

        # TODO: make this constant an option
        if wing_break >= LIMIT_WING_BREAK:
            y_cg = span / 2 * 0.35
            l_cg = (y3_wing - y_cg) / (y3_wing - y2_wing) * (l2_wing - l3_wing) + l3_wing
            el_cg = (y3_wing - y_cg) / (y3_wing - y2_wing) * (
                root_thickness_ratio - kink_thickness_ratio
            ) + kink_thickness_ratio
            front_spar_cg = (y3_wing - y_cg) / (y3_wing - y2_wing) * (
                l2_wing * front_spar_ratio_root - l3_wing * front_spar_ratio_middle
            ) + l3_wing * front_spar_ratio_middle
            rear_spar_cg = (y3_wing - y_cg) / (y3_wing - y2_wing) * (
                l2_wing * rear_spar_ratio_root - l3_wing * rear_spar_ratio_middle
            ) + l3_wing * rear_spar_ratio_middle
            x_cg = (
                (y_cg - y2_wing) / (y3_wing - y2_wing) * x3_wing
                + front_spar_cg
                + (l_cg - front_spar_cg - rear_spar_cg) * 0.7
            )

        else:
            y_cg = span / 2 * 0.35
            l_cg = (y4_wing - y_cg) / (y4_wing - y3_wing) * (l3_wing - l4_wing) + l4_wing
            el_cg = (y4_wing - y_cg) / (y4_wing - y3_wing) * (
                kink_thickness_ratio - tip_thickness_ratio
            ) + tip_thickness_ratio
            front_spar_cg = (y4_wing - y_cg) / (y4_wing - y3_wing) * (
                l3_wing * front_spar_ratio_middle - l4_wing * front_spar_ratio_tip
            ) + l4_wing * front_spar_ratio_tip
            rear_spar_cg = (y4_wing - y_cg) / (y4_wing - y3_wing) * (
                l3_wing * rear_spar_ratio_middle - l4_wing * rear_spar_ratio_tip
            ) + l4_wing * rear_spar_ratio_tip

            x_cg = (
                (y_cg - y3_wing) / (y4_wing - y3_wing) * x4_wing
                + front_spar_cg
                + (l_cg - front_spar_cg - rear_spar_cg) * 0.7
            )

        z_cg = height_max + y_cg * np.sin(dihedral) - el_cg * l_cg / 2.0
        x_cg_absolute = fa_length - 0.25 * x0_wing + (x_cg - x0_wing)

        outputs["data:weight:airframe:wing:CG:x"] = x_cg_absolute
        # This assumes a datum for z CG at the bottom of the fuselage
        outputs["data:weight:airframe:wing:CG:z"] = z_cg
        outputs["data:weight:airframe:wing:CG:thickness"] = el_cg * l_cg
