"""
Estimation of control surfaces center of gravity
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

import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel
from fastoad_cs25.models.weight.cg.cg_components.compute_cg_control_surfaces import (
    ComputeControlSurfacesCG,
)
from fastoad_cs25.models.weight.cg.constants import SERVICE_FLIGHT_CONTROLS_CG

"""
Uses new CS25 models with improved behavior if no kink
"""

RegisterSubmodel.active_models[SERVICE_FLIGHT_CONTROLS_CG] = (
    "rta.submodel.cg.wing.control_surfaces.legacy"
)


@RegisterSubmodel(SERVICE_FLIGHT_CONTROLS_CG, "rta.submodel.cg.wing.control_surfaces.legacy")
class ComputeFlightControlCG(om.Group):
    def setup(self):
        self.add_subsystem("compute_flight_control_cg", ComputeControlSurfacesCG())

    # TODO: harmonize names in between RTA and CS25, cascade changes to cg_ratios and mass_breakdown
    def configure(self):
        self.promotes(
            "compute_flight_control_cg",
            inputs=["*"],
            outputs=[
                (
                    "data:weight:airframe:flight_controls:CG:x",
                    "data:weight:systems:flight_controls:CG:x",
                )
            ],
        )
