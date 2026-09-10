"""
Estimation of center of gravity for load case 2.
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


class ComputeCGLoadCase2(om.ExplicitComponent):
    # TODO: Document equations. Cite sources
    """
    Center of gravity estimation for load case 2:
    add cargo weight (50-50) + fuel weight to OWE.
    """

    def setup(self):
        self.add_input("data:geometry:wing:MAC:length", val=np.nan, units="m")
        self.add_input("data:geometry:wing:MAC:at25percent:x", val=np.nan, units="m")
        self.add_input("data:weight:payload:rear_fret:CG:x", val=np.nan, units="m")
        self.add_input("data:weight:payload:front_fret:CG:x", val=np.nan, units="m")
        self.add_input("data:TLAR:NPAX", val=np.nan, units="unitless")
        self.add_input("data:mission:sizing:fuel", val=np.nan, units="kg")
        self.add_input("data:weight:fuel_tank:CG:x", val=np.nan, units="m")
        self.add_input("data:weight:aircraft:operating_empty:CG:x", val=np.nan, units="m")
        self.add_input("data:weight:aircraft:operating_empty:mass", val=np.nan, units="kg")

        self.add_input(
            "settings:weight:aircraft:payload:design_mass_per_passenger",
            val=np.nan,
            units="kg",
        )
        self.add_input("settings:weight:aircraft:payload:fret_ratio", val=np.nan, units="unitless")

        self.add_output("data:weight:aircraft:load_case_2:CG:MAC_position", units="unitless")
        self.add_output("data:weight:aircraft:load_case_2:CG:index", units="unitless")
        self.add_output("data:weight:aircraft:load_case_2:mass", units="kg")
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        l0_wing = inputs["data:geometry:wing:MAC:length"]
        fa_length = inputs["data:geometry:wing:MAC:at25percent:x"]
        cg_rear_fret = inputs["data:weight:payload:rear_fret:CG:x"]
        cg_front_fret = inputs["data:weight:payload:front_fret:CG:x"]
        npax = inputs["data:TLAR:NPAX"]
        x_cg_plane_aft = inputs["data:weight:aircraft:operating_empty:CG:x"]
        x_cg_plane_down = inputs["data:weight:aircraft:operating_empty:mass"]
        x_cg_plane_up = x_cg_plane_aft * x_cg_plane_down
        fw = inputs["data:mission:sizing:fuel"]
        cg_tank = inputs["data:weight:fuel_tank:CG:x"]

        fret_ratio = inputs["settings:weight:aircraft:payload:fret_ratio"]
        m_pax = inputs["settings:weight:aircraft:payload:design_mass_per_passenger"]

        weight_rear_fret = npax * 0.15 * m_pax * (1 - fret_ratio)
        weight_front_fret = npax * 0.15 * m_pax * fret_ratio
        weight_pl = weight_rear_fret + weight_front_fret
        x_cg_pl_2 = (weight_rear_fret * cg_rear_fret + weight_front_fret * cg_front_fret) / (
            weight_pl
        )
        x_cg_plane_pl_2 = (x_cg_plane_up + weight_pl * x_cg_pl_2 + fw * cg_tank) / (
            x_cg_plane_down + weight_pl + fw
        )  # forward
        cg_ratio_pl_2 = (x_cg_plane_pl_2 - fa_length + 0.25 * l0_wing) / l0_wing

        outputs["data:weight:aircraft:load_case_2:CG:MAC_position"] = cg_ratio_pl_2
        outputs["data:weight:aircraft:load_case_2:CG:index"] = (
            (x_cg_plane_pl_2 - fa_length) * (x_cg_plane_down + weight_pl + fw) / 150.0
        )
        outputs["data:weight:aircraft:load_case_2:mass"] = x_cg_plane_down + weight_pl + fw
