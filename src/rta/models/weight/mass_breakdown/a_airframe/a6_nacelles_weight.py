"""
Estimation of nacelles weight
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
from scipy.constants import pound

from .constants import SERVICE_NACELLE_MASS

RegisterSubmodel.active_models[SERVICE_NACELLE_MASS] = "rta.submodel.weight.mass.airframe.nacelle"


@RegisterSubmodel(SERVICE_NACELLE_MASS, "rta.submodel.weight.mass.airframe.nacelle")
class NacellesWeight(om.ExplicitComponent):
    """
    Weight estimation for nacelle struts

    Based on Roskam Part V, Chap 5, eq 5.33
    """

    def setup(self):
        self.add_input("data:propulsion:RTO_power", val=np.nan, units="hp")
        self.add_input("data:geometry:propulsion:engine:count", val=np.nan, units="unitless")
        self.add_input("tuning:weight:airframe:nacelle:mass:k", val=1.0, units="unitless")
        self.add_input("tuning:weight:airframe:nacelle:mass:offset", val=0.0, units="kg")

        self.add_output("data:weight:airframe:nacelle:mass", units="kg")

        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        rto_power = inputs["data:propulsion:RTO_power"]
        n_engines = inputs["data:geometry:propulsion:engine:count"]
        k_a6 = inputs["tuning:weight:airframe:nacelle:mass:k"]
        offset_a6 = inputs["tuning:weight:airframe:nacelle:mass:offset"]

        temp_a6 = rto_power * n_engines * 0.14 * pound

        outputs["data:weight:airframe:nacelle:mass"] = k_a6 * temp_a6 + offset_a6
