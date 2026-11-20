"""
Placeholder gearbox implementation
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

import numpy as np
from fastoad._utils.arrays import scalarize
from fastoad.model_base.flight_point import FlightPoint, _FieldDescriptor
from fastoad.openmdao.variables import Variable, VariableList

from rta.models.propulsion.component_base import AbstractPropulsiveComponent

INPUT_PARAMETERS = VariableList(
    [
        Variable(
            "data:propulsion:gearbox:efficiency",
            val=np.nan,
            units="unitless",
            desc="Gearbox efficiency (0-1)",
        ),
    ]
)

INPUT_FIELDS = {
    "propeller_shaft_power": _FieldDescriptor(unit="W"),
    "thermal_shaft_power_share": _FieldDescriptor(unit="W"),
}
OUTPUT_FIELDS = {
    "thermal_shaft_power": _FieldDescriptor(unit="W"),
    "electric_shaft_power": _FieldDescriptor(unit="W"),
}


@dataclass
class GearboxComponent(AbstractPropulsiveComponent):
    """
    Placeholder docstring
    """

    name = "GearboxComponent"

    _input_parameters: ClassVar[list] = INPUT_PARAMETERS

    # Dictionary of FlightPoint fields required as input (field_name: unit)
    _input_fields: ClassVar[dict] = INPUT_FIELDS

    # Dictionary of FlightPoint fields to be computed (field_name: unit)
    _output_fields: ClassVar[dict] = OUTPUT_FIELDS

    def compute_single_point_backward(self, flight_point: FlightPoint):
        """
        Placeholder docstring
        """
        output_power = flight_point.propeller_shaft_power
        efficiency = scalarize(
            self.input_parameters["data:propulsion:gearbox:efficiency"].get_val()
        )

        # Simplified control logic for now, will be the interesting and complicated thing to do
        flight_point.thermal_shaft_power = (
            output_power / efficiency * flight_point.thermal_shaft_power_share
        )
        flight_point.electric_shaft_power = (
            output_power / efficiency * (1.0 - flight_point.thermal_shaft_power_share)
        )

    def compute_single_point_forward(self, flight_point: FlightPoint):
        """
        Placeholder docstring
        """
        input_power = flight_point.thermal_shaft_power + flight_point.electric_shaft_power
        efficiency = scalarize(
            self.input_parameters["data:propulsion:gearbox:efficiency"].get_val()
        )

        # Compute output power
        flight_point.propeller_shaft_power = input_power * efficiency
