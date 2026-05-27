"""
Estimation of wing ToC
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


class ComputeToCWingRTA(om.ExplicitComponent):
    # TODO: Document equations. Cite sources
    """Wing ToC estimation

    Reference: Aircraft Design Studies Based on the ATR 72 Author: Mihaela Florentina Niţă
                Eq. (5.10.9)
                http://bibliothek.profscholz.de/
    """

    def setup(self):
        self.add_input("data:TLAR:cruise_mach", val=np.nan)
        self.add_input("data:geometry:wing:sweep_25", val=np.nan, units="deg")

        self.add_output("data:geometry:wing:thickness_ratio")
        self.add_output("data:geometry:wing:root:thickness_ratio")
        self.add_output("data:geometry:wing:kink:thickness_ratio")
        self.add_output("data:geometry:wing:tip:thickness_ratio")

        self.declare_partials("data:geometry:wing:thickness_ratio", "*", method="fd")
        self.declare_partials("data:geometry:wing:root:thickness_ratio", "*", method="fd")
        self.declare_partials("data:geometry:wing:kink:thickness_ratio", "*", method="fd")
        self.declare_partials("data:geometry:wing:tip:thickness_ratio", "*", method="fd")

    def compute(self, inputs, outputs):
        cruise_mach = inputs["data:TLAR:cruise_mach"]
        sweep_25 = inputs["data:geometry:wing:sweep_25"]
        Cl_des = 0.8

        el_aero = (
            0.127
            * cruise_mach ** (-0.204)
            * np.cos(sweep_25 / 180.0 * np.pi) ** 0.573
            * Cl_des**0.065
            * 0.921**0.556
        )
        # Relative thickness
        el_emp = 4.0 / 3 * el_aero
        el_break = el_aero
        el_ext = 2.0 / 3 * el_emp

        outputs["data:geometry:wing:thickness_ratio"] = el_aero
        outputs["data:geometry:wing:root:thickness_ratio"] = el_emp
        outputs["data:geometry:wing:kink:thickness_ratio"] = el_break
        outputs["data:geometry:wing:tip:thickness_ratio"] = el_ext
