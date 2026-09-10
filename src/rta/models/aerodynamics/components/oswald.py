"""
Computation of Oswald coefficient
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
from fastoad_cs25.models.aerodynamics.constants import SERVICE_INDUCED_DRAG_COEFFICIENT

RegisterSubmodel.active_models[SERVICE_INDUCED_DRAG_COEFFICIENT] = (
    "rta.submodel.aerodynamics.induced_drag_coefficient.legacy"
)


@RegisterSubmodel(
    SERVICE_INDUCED_DRAG_COEFFICIENT,
    "rta.submodel.aerodynamics.induced_drag_coefficient.legacy",
)
class InducedDragCoefficient(om.ExplicitComponent):
    """
    Computes the coefficient that should be multiplied by CL**2 to get induced drag.
    Let the dihedral angle appear explicitly as an input variable.
    """

    def initialize(self):
        self.options.declare("low_speed_aero", default=False, types=bool)

    def setup(self):
        self.add_input("data:geometry:wing:area", val=np.nan, units="m**2")
        self.add_input("data:geometry:wing:span", val=np.nan, units="m")
        self.add_input("data:geometry:wing:root:dihedral", val=np.nan, units="rad")

        if self.options["low_speed_aero"]:
            self.add_input(
                "data:aerodynamics:aircraft:low_speed:oswald_coefficient",
                val=np.nan,
                units="unitless",
            )
            self.add_output(
                "data:aerodynamics:aircraft:low_speed:CD:induced:coefficient", units="unitless"
            )
        else:
            self.add_input(
                "data:aerodynamics:aircraft:high_speed:oswald_coefficient",
                val=np.nan,
                units="unitless",
            )
            self.add_output(
                "data:aerodynamics:aircraft:high_speed:CD:induced:coefficient", units="unitless"
            )

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        wing_area = inputs["data:geometry:wing:area"]
        dihedral = inputs["data:geometry:wing:root:dihedral"]
        span = inputs["data:geometry:wing:span"] / np.cos(dihedral)
        aspect_ratio = span**2 / wing_area

        if self.options["low_speed_aero"]:
            coef_e = inputs["data:aerodynamics:aircraft:low_speed:oswald_coefficient"]
        else:
            coef_e = inputs["data:aerodynamics:aircraft:high_speed:oswald_coefficient"]

        coef_k = 1.0 / (np.pi * aspect_ratio * coef_e)

        if self.options["low_speed_aero"]:
            outputs["data:aerodynamics:aircraft:low_speed:CD:induced:coefficient"] = coef_k
        else:
            outputs["data:aerodynamics:aircraft:high_speed:CD:induced:coefficient"] = coef_k
