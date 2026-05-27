"""
Propeller sizing model
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
from fastoad.module_management.constants import ModelDomain
from fastoad.module_management.service_registry import RegisterOpenMDAOSystem
from scipy import constants


@RegisterOpenMDAOSystem("rta.propulsion.propeller_sizing", domain=ModelDomain.PROPULSION)
class Prop_sizing(om.ExplicitComponent):
    """
    Performs sizing of the propeller based on input max power and disk loading.
    """

    def setup(self):
        self.add_input("data:propulsion:propeller:disk_loading", np.nan, units="kW/m**2")
        self.add_input("data:propulsion:propeller:max_power", np.nan, units="kW")

        self.add_output("data:geometry:propulsion:propeller:diameter", units="m")

        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs):
        disk_loading = inputs["data:propulsion:propeller:disk_loading"]
        max_power = inputs["data:propulsion:propeller:max_power"]

        # evaluate propeller diameter
        d = (4 * max_power / (constants.pi * disk_loading)) ** 0.5

        outputs["data:geometry:propulsion:propeller:diameter"] = d
