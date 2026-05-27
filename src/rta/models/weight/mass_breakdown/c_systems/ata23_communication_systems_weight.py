"""
Estimation of communication systems weight
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
from fastoad_cs25.models.weight.mass_breakdown.c_systems.c4_transmissions_systems_weight import (
    TransmissionSystemsWeight,
)

from rta.models.weight.mass_breakdown.c_systems.constants import SERVICE_MASS_ATA23


@RegisterSubmodel(SERVICE_MASS_ATA23, "rta.submodel.mass.system.ata23")
class CommunicationSystemWeightLegacy(om.Group):
    """Weight estimation for communication systems, based on CS25 transmission model"""

    def setup(self):
        self.add_subsystem("communication_system_from_cs25", TransmissionSystemsWeight())

    def configure(self):
        self.promotes(
            "communication_system_from_cs25",
            inputs=[
                "*",
                (
                    "tuning:weight:systems:transmission:mass:k",
                    "tuning:weight:systems:communications:mass:k",
                ),
                (
                    "tuning:weight:systems:transmission:mass:offset",
                    "tuning:weight:systems:communications:mass:offset",
                ),
            ],
            outputs=[
                (
                    "data:weight:systems:transmission:mass",
                    "data:weight:systems:communications:mass",
                )
            ],
        )
