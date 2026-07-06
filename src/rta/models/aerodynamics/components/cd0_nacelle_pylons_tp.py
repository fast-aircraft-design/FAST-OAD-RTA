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

import numpy as np
import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel
from fastoad_cs25.models.aerodynamics.components.utils.friction_drag import (
    get_flat_plate_friction_drag_coefficient,
)
from fastoad_cs25.models.aerodynamics.constants import SERVICE_CD0_NACELLES_PYLONS

RegisterSubmodel.active_models[SERVICE_CD0_NACELLES_PYLONS] = (
    "rta.submodel.aerodynamics.CD0.nacelles"
)


@RegisterSubmodel(SERVICE_CD0_NACELLES_PYLONS, "rta.submodel.aerodynamics.CD0.nacelles")
class Cd0NacelleAndPylonsTP(om.ExplicitComponent):
    def initialize(self):
        self.options.declare("low_speed_aero", default=False, types=bool)

    def setup(self):
        self.low_speed_aero = self.options["low_speed_aero"]

        if self.low_speed_aero:
            self.add_input("data:aerodynamics:aircraft:low_speed:unit_reynolds", val=np.nan)
            self.add_input("data:aerodynamics:aircraft:takeoff:mach", val=np.nan)
            self.add_output("data:aerodynamics:nacelles:low_speed:CD:CD0")
        else:
            self.add_input("data:aerodynamics:aircraft:high_speed:unit_reynolds", val=np.nan)
            self.add_input("data:TLAR:cruise_mach", val=np.nan)
            self.add_output("data:aerodynamics:nacelles:high_speed:CD:CD0")

        self.add_input("data:geometry:propulsion:nacelle:length", val=np.nan, units="m")
        self.add_input("data:geometry:propulsion:pylon:wetted_area", val=np.nan, units="m**2")
        self.add_input("data:geometry:propulsion:nacelle:wetted_area", val=np.nan, units="m**2")
        self.add_input("data:geometry:propulsion:engine:count", val=np.nan)
        self.add_input("data:geometry:wing:area", val=np.nan, units="m**2")

        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs):
        nac_length = inputs["data:geometry:propulsion:nacelle:length"]
        wet_area_nac = inputs["data:geometry:propulsion:nacelle:wetted_area"]
        n_engines = inputs["data:geometry:propulsion:engine:count"]
        wing_area = inputs["data:geometry:wing:area"]
        if self.low_speed_aero:
            mach = inputs["data:aerodynamics:aircraft:takeoff:mach"]
            unit_reynolds = inputs["data:aerodynamics:aircraft:low_speed:unit_reynolds"]
        else:
            mach = inputs["data:TLAR:cruise_mach"]
            unit_reynolds = inputs["data:aerodynamics:aircraft:high_speed:unit_reynolds"]

        cf_nac = get_flat_plate_friction_drag_coefficient(nac_length, mach, unit_reynolds)

        cd0_int_nac = 0.0005  # subject to discussion
        cd0_nac = n_engines * (cf_nac * wet_area_nac / wing_area + cd0_int_nac)

        if self.low_speed_aero:
            outputs["data:aerodynamics:nacelles:low_speed:CD:CD0"] = cd0_nac
        else:
            outputs["data:aerodynamics:nacelles:high_speed:CD:CD0"] = cd0_nac
