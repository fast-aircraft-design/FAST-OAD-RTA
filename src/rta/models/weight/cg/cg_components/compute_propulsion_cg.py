"""
Estimation of propulsion center of gravity
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

from ..constants import SERVICE_PROPULSION_CG

RegisterSubmodel.active_models[SERVICE_PROPULSION_CG] = "rta.submodel.weight.cg.propulsion"


@RegisterSubmodel(SERVICE_PROPULSION_CG, "rta.submodel.weight.cg.propulsion")
class ComputePropulsionCG_RTA(om.ExplicitComponent):
    """Propulsion center of gravity estimation as a function of wing position"""

    def setup(self):
        self.add_input("data:geometry:propulsion:engine:y_ratio", val=np.nan)
        self.add_input("data:geometry:wing:span", val=np.nan, units="m")
        self.add_input("data:geometry:wing:MAC:length", val=np.nan, units="m")
        self.add_input("data:geometry:wing:MAC:leading_edge:x:local", val=np.nan, units="m")
        self.add_input("data:geometry:wing:root:chord", val=np.nan, units="m")
        self.add_input("data:geometry:wing:root:y", val=np.nan, units="m")
        self.add_input("data:geometry:wing:kink:chord", val=np.nan, units="m")
        self.add_input("data:geometry:wing:kink:y", val=np.nan, units="m")
        self.add_input("data:geometry:wing:kink:leading_edge:x:local", val=np.nan, units="m")
        self.add_input("data:geometry:wing:MAC:at25percent:x", val=np.nan, units="m")
        self.add_input("data:geometry:propulsion:nacelle:length", val=np.nan, units="m")

        self.add_output("data:weight:propulsion:engine:CG:x", units="m")
        self.add_output("data:weight:propulsion:propeller:CG:x", units="m")
        self.add_output("data:weight:airframe:nacelle:CG:x", units="m")

        self.declare_partials("data:weight:propulsion:engine:CG:x", "*", method="fd")
        self.declare_partials("data:weight:propulsion:propeller:CG:x", "*", method="fd")
        self.declare_partials("data:weight:airframe:nacelle:CG:x", "*", method="fd")

    def compute(self, inputs, outputs):
        y_ratio_engine = inputs["data:geometry:propulsion:engine:y_ratio"]
        span = inputs["data:geometry:wing:span"]
        l0_wing = inputs["data:geometry:wing:MAC:length"]
        x0_wing = inputs["data:geometry:wing:MAC:leading_edge:x:local"]
        l2_wing = inputs["data:geometry:wing:root:chord"]
        y2_wing = inputs["data:geometry:wing:root:y"]
        l3_wing = inputs["data:geometry:wing:kink:chord"]
        x3_wing = inputs["data:geometry:wing:kink:leading_edge:x:local"]
        y3_wing = inputs["data:geometry:wing:kink:y"]
        fa_length = inputs["data:geometry:wing:MAC:at25percent:x"]
        nac_length = inputs["data:geometry:propulsion:nacelle:length"]

        y_nacelle = y_ratio_engine * span / 2

        l_wing_nac = l3_wing + (l2_wing - l3_wing) * (y3_wing - y_nacelle) / (y3_wing - y2_wing)
        delta_x_nacelle = 0.05 * l_wing_nac
        x_nacelle_cg = (
            x3_wing * (y_nacelle - y2_wing) / (y3_wing - y2_wing)
            - delta_x_nacelle
            - 0.2 * nac_length
        )
        x_nacelle_cg_absolute = fa_length - 0.25 * l0_wing - (x0_wing - x_nacelle_cg)
        outputs["data:weight:propulsion:engine:CG:x"] = x_nacelle_cg_absolute
        outputs["data:weight:propulsion:propeller:CG:x"] = 0.85 * x_nacelle_cg_absolute
        outputs["data:weight:airframe:nacelle:CG:x"] = 1.025 * x_nacelle_cg_absolute
