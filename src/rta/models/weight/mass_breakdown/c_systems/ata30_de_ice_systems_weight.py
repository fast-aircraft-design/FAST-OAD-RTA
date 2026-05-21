"""
Estimation of de-icing systems weight
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
from scipy.constants import degree

from rta.models.weight.mass_breakdown.c_systems.constants import SERVICE_MASS_ATA30


@RegisterSubmodel(SERVICE_MASS_ATA30, "rta.submodel.mass.system.ata30")
class DeIceSystemWeight(om.ExplicitComponent):
    """
    Weight estimation for de-icing systems


    Based on formulas in :cite:`supaero:2014`, mass contribution C23 modified adding horizontal tail
    and removing nacelle contributions.
    """

    def setup(self):
        self.add_input("data:geometry:fuselage:maximum_width", val=np.nan, units="m")
        self.add_input("data:geometry:wing:sweep_0", val=np.nan, units="deg")
        self.add_input("data:geometry:wing:span", val=np.nan, units="m")
        self.add_input("data:geometry:horizontal_tail:sweep_0", val=np.nan, units="deg")
        self.add_input("data:geometry:horizontal_tail:span", val=np.nan, units="m")
        self.add_input("tuning:weight:systems:de-icing:mass:k", val=1.0)
        self.add_input("tuning:weight:systems:de-icing:mass:offset", val=0.0, units="kg")

        self.add_output("data:weight:systems:de-icing:mass", units="kg")

        self.declare_partials("*", "*", method="fd")

    # pylint: disable=too-many-locals
    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        width_max = inputs["data:geometry:fuselage:maximum_width"]
        sweep_leading_edge = inputs["data:geometry:wing:sweep_0"]
        span = inputs["data:geometry:wing:span"]
        sweep_leading_edge_ht = inputs["data:geometry:horizontal_tail:sweep_0"]
        span_ht = inputs["data:geometry:horizontal_tail:span"]
        k = inputs["tuning:weight:systems:de-icing:mass:k"]
        offset = inputs["tuning:weight:systems:de-icing:mass:offset"]

        # Mass of de-icing system
        mass_deice = (
            53
            + 1.9 * (span - width_max) / np.cos(sweep_leading_edge * degree)
            + 1.9 * (span_ht) / np.cos(sweep_leading_edge_ht * degree)
        )
        outputs["data:weight:systems:de-icing:mass"] = k * mass_deice + offset
