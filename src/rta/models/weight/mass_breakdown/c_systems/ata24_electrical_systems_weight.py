"""
Estimation of electrical power systems weight
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

from rta.models.weight.mass_breakdown.c_systems.constants import SERVICE_MASS_ATA24


@RegisterSubmodel(SERVICE_MASS_ATA24, "rta.submodel.mass.system.ata24")
class ElectricalPowerSystemWeight(om.ExplicitComponent):
    """
    Weight estimation for electrical power systems (generation and distribution)

    This includes:

    - Batteries
    - Starter/generators
    - Inverters
    - Control unit
    - Electrical wires for all systems

    Based on formulas in :cite:`supaero:2014`, mass contribution C1
    without flight controls contribution due to mechanical controls
    """

    def setup(self):
        self.add_input("data:geometry:cabin:NPAX1", val=np.nan, units="unitless")
        self.add_input("data:weight:aircraft:MTOW", val=np.nan, units="kg")

        self.add_input(
            "tuning:weight:systems:electric_systems:electric_generation:mass:offset",
            val=0.0,
            units="kg",
        )
        self.add_input(
            "tuning:weight:systems:electric_systems:electric_generation:mass:k",
            val=1.0,
            units="unitless",
        )

        self.add_input(
            "settings:weight:systems:electric_systems:mass:k_elec", val=1.0, units="unitless"
        )

        self.add_output("data:weight:systems:electric_systems:electric_generation:mass", units="kg")
        self.add_output(
            "data:weight:systems:electric_systems:electric_common_installation:mass",
            units="kg",
        )

        self.declare_partials("*", "*", method="fd")

    # pylint: disable=too-many-locals
    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        npax1 = inputs["data:geometry:cabin:NPAX1"]
        mtow = inputs["data:weight:aircraft:MTOW"]

        k = inputs["tuning:weight:systems:electric_systems:electric_generation:mass:k"]
        offset = inputs["tuning:weight:systems:electric_systems:electric_generation:mass:offset"]

        k_elec = inputs["settings:weight:systems:electric_systems:mass:k_elec"]

        # Mass of electric system
        m_elec = (k_elec * (0.444 * mtow**0.66 + 2.54 * npax1)) * k + offset
        outputs["data:weight:systems:electric_systems:electric_generation:mass"] = m_elec * 0.6
        outputs["data:weight:systems:electric_systems:electric_common_installation:mass"] = (
            m_elec * 0.4
        )
