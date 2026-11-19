"""
Estimation of global center of gravity
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

import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel
from fastoad_cs25.models.weight.cg.constants import (
    SERVICE_EMPTY_AIRCRAFT_CG_Y,
    SERVICE_EMPTY_AIRCRAFT_CG_Z,
    SERVICE_GLOBAL_CG,
)

from .compute_cg_loadcase1 import ComputeCGLoadCase1
from .compute_cg_loadcase2 import ComputeCGLoadCase2
from .compute_cg_loadcase3 import ComputeCGLoadCase3
from .compute_cg_ratio_aft import ComputeCGXRatioAft
from .compute_max_cg_ratio import ComputeMaxCGratio

RegisterSubmodel.active_models[SERVICE_GLOBAL_CG] = "rta.submodel.weight.cg.global.legacy"


@RegisterSubmodel(SERVICE_GLOBAL_CG, "rta.submodel.weight.cg.global.legacy")
class ComputeGlobalCG(om.Group):
    # TODO: Document equations. Cite sources
    """Global center of gravity estimation"""

    def setup(self):
        self.add_subsystem("cg_ratio_aft", ComputeCGXRatioAft(), promotes=["*"])

        cg_item_names = [
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
        ]

        self.add_subsystem(
            "cg_empty_y",
            RegisterSubmodel.get_submodel(
                SERVICE_EMPTY_AIRCRAFT_CG_Y, options={"cg_y_item_names": cg_item_names}
            ),
            promotes=["*"],
        )
        self.add_subsystem(
            "cg_empty_z",
            RegisterSubmodel.get_submodel(
                SERVICE_EMPTY_AIRCRAFT_CG_Z, options={"cg_z_item_names": cg_item_names}
            ),
            promotes=["*"],
        )

        self.add_subsystem("cg_ratio_lc1", ComputeCGLoadCase1(), promotes=["*"])
        self.add_subsystem("cg_ratio_lc2", ComputeCGLoadCase2(), promotes=["*"])
        self.add_subsystem("cg_ratio_lc3", ComputeCGLoadCase3(), promotes=["*"])
        self.add_subsystem("cg_ratio_max", ComputeMaxCGratio(), promotes=["*"])
