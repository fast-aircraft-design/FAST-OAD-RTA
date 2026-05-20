"""
FAST - Copyright (c) 2025 ONERA ISAE
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
    SERVICE_AIRCRAFT_CG,
    SERVICE_FLIGHT_CONTROLS_CG,
    SERVICE_GLOBAL_CG,
    SERVICE_HORIZONTAL_TAIL_CG,
    SERVICE_MLG_CG,
    SERVICE_OTHERS_CG,
    SERVICE_TANKS_CG,
    SERVICE_VERTICAL_TAIL_CG,
    SERVICE_WING_CG,
)
from fastoad_cs25.models.weight.constants import SERVICE_CENTERS_OF_GRAVITY

from .constants import SERVICE_PROPULSION_CG

RegisterSubmodel.active_models[SERVICE_CENTERS_OF_GRAVITY] = "rta.submodel.weight.cg.legacy"


@RegisterSubmodel(SERVICE_CENTERS_OF_GRAVITY, "rta.submodel.weight.cg.legacy")
class CG(om.Group):
    """Model that computes the global center of gravity"""

    def __init__(self):
        super().__init__()

    def setup(self):
        self.add_subsystem(
            "ht_cg",
            RegisterSubmodel.get_submodel(SERVICE_HORIZONTAL_TAIL_CG),
            promotes=["*"],
        )
        self.add_subsystem(
            "vt_cg",
            RegisterSubmodel.get_submodel(SERVICE_VERTICAL_TAIL_CG),
            promotes=["*"],
        )
        self.add_subsystem(
            "compute_cg_wing",
            RegisterSubmodel.get_submodel(SERVICE_WING_CG),
            promotes=["*"],
        )
        self.add_subsystem(
            "compute_cg_flight_controls",
            RegisterSubmodel.get_submodel(SERVICE_FLIGHT_CONTROLS_CG),
            promotes=["*"],
        )
        self.add_subsystem(
            "compute_cg_tanks",
            RegisterSubmodel.get_submodel(SERVICE_TANKS_CG),
            promotes=["*"],
        )
        self.add_subsystem(
            "compute_cg_propulsion",
            RegisterSubmodel.get_submodel(SERVICE_PROPULSION_CG),
            promotes=["*"],
        )
        self.add_subsystem(
            "compute_cg_others",
            RegisterSubmodel.get_submodel(SERVICE_OTHERS_CG),
            promotes=["*"],
        )
        self.add_subsystem(
            "compute_cg",
            RegisterSubmodel.get_submodel(SERVICE_GLOBAL_CG),
            promotes=["*"],
        )
        self.add_subsystem(
            "update_mlg", RegisterSubmodel.get_submodel(SERVICE_MLG_CG), promotes=["*"]
        )

        self.add_subsystem(
            "aircraft",
            RegisterSubmodel.get_submodel(SERVICE_AIRCRAFT_CG),
            promotes=["*"],
        )
