"""
Estimation of center of gravity for load case 1.
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


class ComputeCGLoadCase1(om.ExplicitComponent):
    # TODO: Document equations. Cite sources
    """Center of gravity estimation for load case 1: add fuel to OWE"""

    def setup(self):
        self.add_input("data:geometry:wing:MAC:length", val=np.nan, units="m")
        self.add_input("data:geometry:wing:MAC:at25percent:x", val=np.nan, units="m")
        self.add_input("data:mission:sizing:fuel", val=np.nan, units="kg")
        self.add_input("data:weight:fuel_tank:CG:x", val=np.nan, units="m")
        self.add_input("data:weight:aircraft:operating_empty:CG:x", val=np.nan, units="m")
        self.add_input("data:weight:aircraft:operating_empty:mass", val=np.nan, units="kg")

        self.add_output("data:weight:aircraft:load_case_1:CG:MAC_position", units="unitless")
        self.add_output("data:weight:aircraft:load_case_1:CG:index", units="unitless")
        self.add_output("data:weight:aircraft:load_case_1:mass", units="kg")

        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        fw = inputs["data:mission:sizing:fuel"]
        cg_tank = inputs["data:weight:fuel_tank:CG:x"]
        l0_wing = inputs["data:geometry:wing:MAC:length"]
        fa_length = inputs["data:geometry:wing:MAC:at25percent:x"]
        x_cg_plane_aft = inputs["data:weight:aircraft:operating_empty:CG:x"]
        x_cg_plane_down = inputs["data:weight:aircraft:operating_empty:mass"]
        x_cg_plane_up = x_cg_plane_aft * x_cg_plane_down

        # TODO: factorize the four load cases as they are relatively similar

        weight_pl = fw
        x_cg_pl_1 = cg_tank
        x_cg_plane_pl_1 = (x_cg_plane_up + weight_pl * x_cg_pl_1) / (
            x_cg_plane_down + weight_pl
        )  # forward
        cg_ratio_pl_1 = (x_cg_plane_pl_1 - fa_length + 0.25 * l0_wing) / l0_wing

        outputs["data:weight:aircraft:load_case_1:CG:MAC_position"] = cg_ratio_pl_1
        outputs["data:weight:aircraft:load_case_1:CG:index"] = (
            (x_cg_plane_pl_1 - fa_length) * (x_cg_plane_down + weight_pl) / 150.0
        )
        outputs["data:weight:aircraft:load_case_1:mass"] = x_cg_plane_down + weight_pl
