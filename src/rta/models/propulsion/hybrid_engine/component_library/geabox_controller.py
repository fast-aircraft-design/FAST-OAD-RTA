"""
Placeholder gearbox controller implementation
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

from fastoad.model_base.flight_point import FlightPoint, _FieldDescriptor

from rta.models.propulsion.component_base import AbstractPropulsiveComponent

INPUT_PARAMETERS = {}
INPUT_FIELDS = {
    "propeller_shaft_power": _FieldDescriptor(unit="W"),
}
OUTPUT_FIELDS = {
    "thermal_shaft_power_share": _FieldDescriptor(unit="W"),  # Added here so that it is
}


@dataclass
class GearboxControllerComponent(AbstractPropulsiveComponent):
    """
    Placeholder docstring
    """

    name = "GearboxControllerComponent"

    _input_parameters: ClassVar[list] = INPUT_PARAMETERS

    # Dictionary of FlightPoint fields required as input (field_name: unit)
    _input_fields: ClassVar[dict] = INPUT_FIELDS

    # Dictionary of FlightPoint fields to be computed (field_name: unit)
    _output_fields: ClassVar[dict] = OUTPUT_FIELDS

    def compute_single_point_backward(self, flight_point: FlightPoint):
        """
        Placeholder docstring
        """

        flight_point.thermal_shaft_power_share = 0.9

    def compute_single_point_forward(self, flight_point: FlightPoint):
        """
        Placeholder docstring
        """

        pass
