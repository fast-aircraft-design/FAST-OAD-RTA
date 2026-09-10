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

from rta.models.aerodynamics.constants import ALPHA_POINT_COUNT

"""
Undocumented
"""


class ComputeDeltaLg(om.ExplicitComponent):
    """Computes landing gear extension effect on Cl and Cd"""

    def initialize(self):
        self.options.declare("landing_flag", default=False, types=bool)

    def setup(self):
        if self.options["landing_flag"]:
            self.add_output(
                "data:aerodynamics:aircraft:landing:lg_effect:DCL",
                shape=ALPHA_POINT_COUNT,
                units="unitless",
            )
            self.add_output(
                "data:aerodynamics:aircraft:landing:lg_effect:DCD",
                shape=ALPHA_POINT_COUNT,
                units="unitless",
            )
        else:
            self.add_output(
                "data:aerodynamics:aircraft:takeoff:lg_effect:DCL",
                shape=ALPHA_POINT_COUNT,
                units="unitless",
            )
            self.add_output(
                "data:aerodynamics:aircraft:takeoff:lg_effect:DCD",
                shape=ALPHA_POINT_COUNT,
                units="unitless",
            )

    def compute(self, inputs, outputs):
        if self.options["landing_flag"]:
            outputs["data:aerodynamics:aircraft:landing:lg_effect:DCL"] = (
                np.ones(ALPHA_POINT_COUNT) * 0.02
            )
            outputs["data:aerodynamics:aircraft:landing:lg_effect:DCD"] = (
                np.ones(ALPHA_POINT_COUNT) * 0.02
            )
        else:
            outputs["data:aerodynamics:aircraft:takeoff:lg_effect:DCL"] = (
                np.ones(ALPHA_POINT_COUNT) * 0.02
            )
            outputs["data:aerodynamics:aircraft:takeoff:lg_effect:DCD"] = (
                np.ones(ALPHA_POINT_COUNT) * 0.02
            )
