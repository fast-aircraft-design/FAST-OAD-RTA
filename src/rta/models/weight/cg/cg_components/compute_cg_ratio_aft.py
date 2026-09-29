"""
Estimation of center of gravity ratio with aft
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
from fastoad_cs25.models.weight.cg.cg_components.compute_cg_ratio_aft import ComputeCGX


class ComputeCGXRatioAft(om.Group):
    def initialize(self):
        self.options.declare(
            "cg_x_item_names",
            default=[
                "data:weight:airframe:wing:",
                "data:weight:airframe:fuselage:",
                "data:weight:airframe:horizontal_tail:",
                "data:weight:airframe:vertical_tail:",
                "data:weight:airframe:landing_gear:main:",
                "data:weight:airframe:landing_gear:front:",
                "data:weight:airframe:nacelle:",
                "data:weight:propulsion:engine:",
                "data:weight:propulsion:propeller:",
                "data:weight:propulsion:engine_controls_instrumentation:",
                "data:weight:propulsion:fuel_lines:",
                "data:weight:systems:auxiliary_power_unit:",
                "data:weight:systems:electric_systems:electric_generation:",
                "data:weight:systems:electric_systems:electric_common_installation:",
                "data:weight:systems:hydraulic_systems:",
                "data:weight:systems:fire_protection:",
                "data:weight:systems:flight_furnishing:",
                "data:weight:systems:automatic_flight_system:",
                "data:weight:systems:communications:",
                "data:weight:systems:ECS:",
                "data:weight:systems:de-icing:",
                "data:weight:systems:navigation:",
                "data:weight:systems:flight_controls:",
                "data:weight:furniture:furnishing:",
                "data:weight:furniture:water:",
                "data:weight:furniture:interior_integration:",
                "data:weight:furniture:insulation:",
                "data:weight:furniture:cabin_lighting:",
                "data:weight:furniture:seats_crew_accommodation:",
                "data:weight:furniture:oxygen:",
                "data:weight:operational:items:passenger_seats:",
                "data:weight:operational:items:unusable_fuel:",
                "data:weight:operational:items:documents_toolkit:",
                "data:weight:operational:items:galley_structure:",
                "data:weight:operational:equipment:others:",
            ],
        )

    def setup(self):
        self.add_subsystem(
            "cg_x_all", ComputeCGX(cg_x_item_names=self.options["cg_x_item_names"]), promotes=["*"]
        )
        self.add_subsystem("cg_x_operating_empty", ComputeCGXOperatingEmpty(), promotes=["*"])
        self.add_subsystem("cg_x_ratio", CGXRatio(), promotes=["*"])


class ComputeCGXOperatingEmpty(om.ExplicitComponent):
    def setup(self):
        self.add_input("data:weight:operational:equipment:crew:mass", val=np.nan, units="kg")
        self.add_input("data:weight:operational:equipment:crew:CG:x", val=np.nan, units="m")
        self.add_input("data:weight:aircraft_empty:mass", val=np.nan, units="kg")
        self.add_input("data:weight:aircraft_empty:CG:x", val=np.nan, units="m")

        self.add_output("data:weight:aircraft:operating_empty:CG:x", units="m")
        self.add_output("data:weight:aircraft:operating_empty:mass", units="kg")

    def setup_partials(self):
        self.declare_partials("data:weight:aircraft:operating_empty:CG:x", "*", method="exact")
        self.declare_partials(
            "data:weight:aircraft:operating_empty:mass",
            ["data:weight:operational:equipment:crew:mass", "data:weight:aircraft_empty:mass"],
            val=1.0,
        )

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):

        crew_mass = inputs["data:weight:operational:equipment:crew:mass"]
        crew_cg = inputs["data:weight:operational:equipment:crew:CG:x"]
        empty_aircraft_mass = inputs["data:weight:aircraft_empty:mass"]
        empty_aircraft_cg = inputs["data:weight:aircraft_empty:CG:x"]

        outputs["data:weight:aircraft:operating_empty:mass"] = empty_aircraft_mass + crew_mass
        outputs["data:weight:aircraft:operating_empty:CG:x"] = (
            empty_aircraft_mass * empty_aircraft_cg + crew_mass * crew_cg
        ) / (empty_aircraft_mass + crew_mass)

    def compute_partials(self, inputs, partials, discrete_inputs=None):
        crew_mass = inputs["data:weight:operational:equipment:crew:mass"]
        crew_cg = inputs["data:weight:operational:equipment:crew:CG:x"]
        empty_aircraft_mass = inputs["data:weight:aircraft_empty:mass"]
        empty_aircraft_cg = inputs["data:weight:aircraft_empty:CG:x"]

        partials[
            "data:weight:aircraft:operating_empty:CG:x",
            "data:weight:operational:equipment:crew:mass",
        ] = (crew_cg * empty_aircraft_mass - empty_aircraft_mass * empty_aircraft_cg) / (
            empty_aircraft_mass + crew_mass
        ) ** 2.0
        partials[
            "data:weight:aircraft:operating_empty:CG:x",
            "data:weight:aircraft_empty:mass",
        ] = (empty_aircraft_cg * crew_mass - crew_mass * crew_cg) / (
            empty_aircraft_mass + crew_mass
        ) ** 2.0
        partials[
            "data:weight:aircraft:operating_empty:CG:x",
            "data:weight:operational:equipment:crew:CG:x",
        ] = crew_mass / (empty_aircraft_mass + crew_mass)
        partials["data:weight:aircraft:operating_empty:CG:x", "data:weight:aircraft_empty:CG:x"] = (
            empty_aircraft_mass / (empty_aircraft_mass + crew_mass)
        )


class CGXRatio(om.ExplicitComponent):
    def setup(self):
        self.add_input("data:weight:aircraft:operating_empty:CG:x", val=np.nan, units="m")
        self.add_input("data:geometry:wing:MAC:length", val=np.nan, units="m")
        self.add_input("data:geometry:wing:MAC:at25percent:x", val=np.nan, units="m")
        self.add_input("data:weight:aircraft:operating_empty:mass", units="kg")

        self.add_output("data:weight:aircraft:operating_empty:CG:MAC_position", units="unitless")
        self.add_output("data:weight:aircraft:operating_empty:CG:index", units="unitless")

    def setup_partials(self):
        self.declare_partials(
            of="data:weight:aircraft:operating_empty:CG:MAC_position",
            wrt=[
                "data:weight:aircraft:operating_empty:CG:x",
                "data:geometry:wing:MAC:length",
                "data:geometry:wing:MAC:at25percent:x",
            ],
            method="exact",
        )
        self.declare_partials(
            of="data:weight:aircraft:operating_empty:CG:index",
            wrt=[
                "data:weight:aircraft:operating_empty:CG:x",
                "data:weight:aircraft:operating_empty:mass",
                "data:geometry:wing:MAC:at25percent:x",
            ],
            method="exact",
        )

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        x_cg_all = inputs["data:weight:aircraft:operating_empty:CG:x"]
        wing_position = inputs["data:geometry:wing:MAC:at25percent:x"]
        mac = inputs["data:geometry:wing:MAC:length"]
        operating_empty_mass = inputs["data:weight:aircraft:operating_empty:mass"]

        outputs["data:weight:aircraft:operating_empty:CG:MAC_position"] = (
            x_cg_all - wing_position + 0.25 * mac
        ) / mac
        outputs["data:weight:aircraft:operating_empty:CG:index"] = (
            (x_cg_all - wing_position) * operating_empty_mass / 150
        )

    def compute_partials(self, inputs, partials, discrete_inputs=None):
        x_cg_all = inputs["data:weight:aircraft:operating_empty:CG:x"]
        wing_position = inputs["data:geometry:wing:MAC:at25percent:x"]
        mac = inputs["data:geometry:wing:MAC:length"]
        operating_empty_mass = inputs["data:weight:aircraft:operating_empty:mass"]

        partials[
            "data:weight:aircraft:operating_empty:CG:MAC_position",
            "data:weight:aircraft:operating_empty:CG:x",
        ] = 1.0 / mac
        partials[
            "data:weight:aircraft:operating_empty:CG:MAC_position",
            "data:geometry:wing:MAC:at25percent:x",
        ] = -1.0 / mac
        partials[
            "data:weight:aircraft:operating_empty:CG:MAC_position", "data:geometry:wing:MAC:length"
        ] = -(x_cg_all - wing_position) / mac**2.0

        partials[
            "data:weight:aircraft:operating_empty:CG:index",
            "data:weight:aircraft:operating_empty:CG:x",
        ] = operating_empty_mass / 150
        partials[
            "data:weight:aircraft:operating_empty:CG:index", "data:geometry:wing:MAC:at25percent:x"
        ] = -operating_empty_mass / 150
        partials[
            "data:weight:aircraft:operating_empty:CG:index",
            "data:weight:aircraft:operating_empty:mass",
        ] = (x_cg_all - wing_position) / 150
