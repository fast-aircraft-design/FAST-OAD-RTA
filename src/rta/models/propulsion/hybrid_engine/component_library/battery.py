"""
Placeholder battery implementation
"""

#  This file is part of FAST-OAD : A framework for rapid Overall Aircraft Design
#  Copyright (C) 2026 ONERA & ISAE-SUPAERO
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

from dataclasses import dataclass
from typing import ClassVar

import fastoad.api as oad
import numpy as np
from fastoad._utils.arrays import scalarize
from fastoad.model_base.flight_point import FlightPoint, _FieldDescriptor
from fastoad.openmdao.variables import Variable, VariableList

from rta.models.propulsion.component_base import AbstractPropulsiveComponent

INPUT_PARAMETERS = VariableList(
    [
        Variable(
            "data:propulsion:battery:rated_energy",
            val=np.nan,
            units="W*h",
            desc="Battery rated energy",
        ),
        Variable(
            "data:propulsion:battery:rated_power",
            val=np.nan,
            units="W",
            desc="Battery rated power",
        ),
    ]
)

INPUT_FIELDS = {
    "electric_dc_power": _FieldDescriptor(unit="W"),
}
OUTPUT_FIELDS = {
    "battery_soc_derivative": _FieldDescriptor(unit="W"),
    "battery_power_rate": _FieldDescriptor(unit="unitless"),
}
# Needs to be added using the add_field mechanism as we can't provide a default value otherwise
oad.FlightPoint.add_field(
    "battery_soc",
    unit="unitless",
    default_value=100.0,
    is_cumulative=True,
    integrates_from="battery_soc_derivative",
)


@dataclass
class BatteryComponent(AbstractPropulsiveComponent):
    """
    Placeholder docstring
    """

    name = "BatteryComponent"

    _input_parameters: ClassVar[list] = INPUT_PARAMETERS

    # Dictionary of FlightPoint fields required as input (field_name: unit)
    _input_fields: ClassVar[dict] = INPUT_FIELDS

    # Dictionary of FlightPoint fields to be computed (field_name: unit)
    _output_fields: ClassVar[dict] = OUTPUT_FIELDS

    def compute_single_point_backward(self, flight_point: FlightPoint):
        """
        Placeholder docstring
        """
        output_power = flight_point.electric_dc_power
        max_power = scalarize(
            self.input_parameters["data:propulsion:battery:rated_power"].get_val()
        )
        battery_energy_joules = (
            scalarize(self.input_parameters["data:propulsion:battery:rated_energy"].get_val())
            * 3600.0
        )

        flight_point.battery_soc_derivative = -output_power / battery_energy_joules
        flight_point.battery_power_rate = output_power / max_power

    def compute_single_point_forward(self, flight_point: FlightPoint):
        """
        Placeholder docstring
        """
        max_power = scalarize(
            self.input_parameters["data:propulsion:battery:rated_power"].get_val()
        )
        battery_energy_joules = (
            scalarize(self.input_parameters["data:propulsion:battery:rated_energy"].get_val())
            * 3600.0
        )
        output_power = flight_point.battery_power_rate * max_power

        # Compute output power
        flight_point.electric_dc_power = output_power
        flight_point.battery_soc_derivative = -output_power / battery_energy_joules
