"""
Estimation of crew weight
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


class OperationalEquipmentsWeight(om.ExplicitComponent):
    """
    Weight estimation for aircraft operational equipment. It includes:

        - Emergency equipment
        - Fluids/ engine oil
        - Drinkable water
        - Crew

    """

    def setup(self):
        self.add_input("data:geometry:cabin:crew_count:technical", val=np.nan)
        self.add_input("data:geometry:cabin:crew_count:commercial", val=np.nan)
        self.add_input(
            "settings:weight:operational:equipment:mass_per_crew:commercial", val=75, units="kg"
        )
        self.add_input(
            "settings:weight:operational:equipment:mass_per_crew:technical", val=85, units="kg"
        )
        self.add_input(
            "settings:weight:operational:equipment:others",
            val=100,
            units="kg",
            desc="Lump-sum mass for other small operational items.",
        )

        self.add_output("data:weight:operational:equipment:crew:mass", units="kg")
        self.add_output("data:weight:operational:equipment:others:mass", units="kg")

        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        cockpit_crew = inputs["data:geometry:cabin:crew_count:technical"]
        cabin_crew = inputs["data:geometry:cabin:crew_count:commercial"]

        mass_per_crew_commercial = inputs[
            "settings:weight:operational:equipment:mass_per_crew:commercial"
        ]
        mass_per_crew_technical = inputs[
            "settings:weight:operational:equipment:mass_per_crew:technical"
        ]
        others = inputs["settings:weight:operational:equipment:others"]

        crew_mass = mass_per_crew_technical * cockpit_crew + mass_per_crew_commercial * cabin_crew

        outputs["data:weight:operational:equipment:crew:mass"] = crew_mass
        outputs["data:weight:operational:equipment:others:mass"] = others
