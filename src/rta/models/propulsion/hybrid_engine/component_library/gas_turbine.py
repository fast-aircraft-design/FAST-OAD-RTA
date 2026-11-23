"""
Placeholder gas turbine implementation
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
            "data:propulsion:gas_turbine:sfc",
            val=np.nan,
            units="kg/W/s",
            desc="Gas turbine sfc",
        ),
        Variable(
            "data:propulsion:gas_turbine:rto_power",
            val=np.nan,
            units="W",
            desc="Gas turbine rated takeoff power",
        ),
    ]
)

INPUT_FIELDS = {
    "thermal_shaft_power": _FieldDescriptor(unit="W"),
}
OUTPUT_FIELDS = {
    "psfc": _FieldDescriptor(unit="kg/W/s"),
    "fuel_flow": _FieldDescriptor(unit="kg/s"),
    "gas_turbine_power_rate": _FieldDescriptor(unit="unitless"),
}


@dataclass
class GasTurbineComponent(AbstractPropulsiveComponent):
    """
    Placeholder docstring
    """

    name = "GasTurbineComponent"

    _input_parameters: ClassVar[list] = INPUT_PARAMETERS

    # Dictionary of FlightPoint fields required as input (field_name: unit)
    _input_fields: ClassVar[dict] = INPUT_FIELDS

    # Dictionary of FlightPoint fields to be computed (field_name: unit)
    _output_fields: ClassVar[dict] = OUTPUT_FIELDS

    def compute_single_point_backward(self, flight_point: FlightPoint):
        """
        Placeholder docstring
        """
        output_power = flight_point.thermal_shaft_power
        psfc = scalarize(self.input_parameters["data:propulsion:gas_turbine:sfc"].get_val())
        max_power = scalarize(
            self.input_parameters["data:propulsion:gas_turbine:rto_power"].get_val()
        )
        fuel_flow = output_power * psfc

        flight_point.psfc = psfc
        flight_point.fuel_flow = fuel_flow
        flight_point.gas_turbine_power_rate = output_power / max_power

    def compute_single_point_forward(self, flight_point: FlightPoint):
        """
        Placeholder docstring
        """
        max_power = scalarize(
            self.input_parameters["data:propulsion:gas_turbine:rto_power"].get_val()
        )
        psfc = scalarize(self.input_parameters["data:propulsion:gas_turbine:sfc"].get_val())
        output_power = flight_point.gas_turbine_power_rate * max_power
        fuel_flow = output_power * psfc

        # Compute output power
        flight_point.thermal_shaft_power = output_power
        flight_point.fuel_flow = fuel_flow
        flight_point.psfc = psfc

        # Actual SFC needs to be computed outside, once the thrust is known
