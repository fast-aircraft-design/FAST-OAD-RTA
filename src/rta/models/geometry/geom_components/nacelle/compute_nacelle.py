"""
Estimation of nacelle and pylon geometry
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
import scipy.constants as constants
from fastoad.module_management.service_registry import RegisterSubmodel
from fastoad_cs25.models.geometry.constants import SERVICE_NACELLE_PYLON_GEOMETRY

RegisterSubmodel.active_models[SERVICE_NACELLE_PYLON_GEOMETRY] = "rta.submodel.geometry.nacelles"


@RegisterSubmodel(SERVICE_NACELLE_PYLON_GEOMETRY, "rta.submodel.geometry.nacelles")
class ComputeNacelleGeometry(om.ExplicitComponent):
    # TODO: Document equations. Cite sources
    """Nacelle geometry estimation"""

    def setup(self):
        self.add_input("data:geometry:propulsion:engine:y_ratio", val=np.nan)
        self.add_input("data:geometry:wing:span", val=np.nan, units="m")
        self.add_input("data:propulsion:design_thermal_power", np.nan, units="W")
        self.add_input("data:propulsion:electric_systems:design_electric_power", 0, units="W")

        self.add_output("data:geometry:propulsion:nacelle:length", units="m")
        self.add_output("data:geometry:propulsion:nacelle:diameter", units="m")
        self.add_output("data:geometry:propulsion:nacelle:y", units="m")
        self.add_output("data:geometry:propulsion:nacelle:wetted_area", units="m**2")

        self.declare_partials(
            "data:geometry:propulsion:nacelle:diameter",
            [
                "data:propulsion:design_thermal_power",
                "data:propulsion:electric_systems:design_electric_power",
            ],
            method="fd",
        )
        self.declare_partials(
            "data:geometry:propulsion:nacelle:length",
            [
                "data:propulsion:design_thermal_power",
                "data:propulsion:electric_systems:design_electric_power",
            ],
            method="fd",
        )

        self.declare_partials(
            "data:geometry:propulsion:nacelle:y",
            [
                "data:geometry:propulsion:engine:y_ratio",
                "data:geometry:wing:span",
            ],
            method="fd",
        )

        self.declare_partials(
            "data:geometry:propulsion:nacelle:wetted_area",
            [
                "data:propulsion:design_thermal_power",
                "data:propulsion:electric_systems:design_electric_power",
            ],
            method="fd",
        )

    def compute(self, inputs, outputs):
        y_ratio_engine = inputs["data:geometry:propulsion:engine:y_ratio"]
        span = inputs["data:geometry:wing:span"]
        design_thermal_power = inputs["data:propulsion:design_thermal_power"]
        design_electric_power = inputs["data:propulsion:electric_systems:design_electric_power"]

        # calculation of gas turbine dimensions
        nac_length = (
            4.14
            * ((design_thermal_power + design_electric_power) / constants.hp) ** 0.373
            * constants.inch
        )
        nac_dia = (
            9.48
            * ((design_thermal_power + design_electric_power) / constants.hp) ** 0.12
            * constants.inch
        )

        outputs["data:geometry:propulsion:nacelle:length"] = nac_length
        outputs["data:geometry:propulsion:nacelle:diameter"] = nac_dia

        y_nacell = y_ratio_engine * span / 2
        outputs["data:geometry:propulsion:nacelle:y"] = y_nacell

        # Wet surfaces
        wet_area_nac = np.pi * nac_dia * nac_length

        outputs["data:geometry:propulsion:nacelle:wetted_area"] = wet_area_nac
