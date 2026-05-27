"""Main components for mass breakdown."""
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
from fastoad_cs25.models.weight.mass_breakdown.constants import (
    SERVICE_AIRFRAME_MASS,
    SERVICE_FURNITURE_MASS,
    SERVICE_OWE,
    SERVICE_PROPULSION_MASS,
    SERVICE_SYSTEMS_MASS,
)

from rta.models.weight.mass_breakdown.constants import SERVICE_OPERATIONAL_MASS

RegisterSubmodel.active_models[SERVICE_OWE] = "rta.weight.owe.legacy"


@RegisterSubmodel(SERVICE_OWE, "rta.weight.owe.legacy")
class OperatingWeightEmpty(om.Group):
    """Operating Empty Weight (OEW) estimation.

    This group aggregates weight from all components of the aircraft.
    """

    def setup(self):
        # Propulsion should be done before airframe, because it drives nacelle mass.
        self.add_subsystem(
            "propulsion_weight",
            RegisterSubmodel.get_submodel(SERVICE_PROPULSION_MASS),
            promotes=["*"],
        )
        self.add_subsystem(
            "airframe_weight",
            RegisterSubmodel.get_submodel(SERVICE_AIRFRAME_MASS),
            promotes=["*"],
        )
        self.add_subsystem(
            "systems_weight",
            RegisterSubmodel.get_submodel(SERVICE_SYSTEMS_MASS),
            promotes=["*"],
        )
        self.add_subsystem(
            "furniture_weight",
            RegisterSubmodel.get_submodel(SERVICE_FURNITURE_MASS),
            promotes=["*"],
        )
        self.add_subsystem(
            "operational_weight",
            RegisterSubmodel.get_submodel(SERVICE_OPERATIONAL_MASS),
            promotes=["*"],
        )

        weight_sum = om.AddSubtractComp()
        weight_sum.add_equation(
            "data:weight:aircraft:OWE",
            [
                "data:weight:airframe:mass",
                "data:weight:propulsion:mass",
                "data:weight:systems:mass",
                "data:weight:furniture:mass",
                "data:weight:operational:mass",
            ],
            units="kg",
            desc="OWE",
        )

        self.add_subsystem("OWE_sum", weight_sum, promotes=["*"])
