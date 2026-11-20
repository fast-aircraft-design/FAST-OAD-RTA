"""
Placeholder propeller implementation
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
            "data:propulsion:propeller:efficiency",
            val=np.nan,
            units="unitless",
            desc="Propeller efficiency (0-1)",
        ),
        Variable(
            "data:propulsion: propeller:rated_power",
            val=np.nan,
            units="kw",
            desc="Propeller maximum power",
        ),
    ]
)

INPUT_FIELDS = {
    "thrust": _FieldDescriptor(unit="N"),
    "true_airspeed": _FieldDescriptor(unit="m/s"),
}

OUTPUT_FIELDS = {
    "propeller_shaft_power": _FieldDescriptor(unit="W", is_cumulative=False),
    "propeller_power_rate": _FieldDescriptor(unit="unitless", is_cumulative=False),
}


@dataclass
class PropellerComponent(AbstractPropulsiveComponent):
    """
    Placeholder docstring
    """

    name = "PropellerComponent"

    _input_parameters: ClassVar[list] = INPUT_PARAMETERS

    # Dictionary of FlightPoint fields required as input (field_name: unit)
    _input_fields: ClassVar[dict] = INPUT_FIELDS

    # Dictionary of FlightPoint fields to be computed (field_name: unit)
    _output_fields: ClassVar[dict] = OUTPUT_FIELDS

    def compute_single_point_backward(self, flight_point: FlightPoint):
        """
        Placeholder docstring
        """
        thrust = flight_point.thrust
        true_airspeed = flight_point.true_airspeed
        efficiency = scalarize(
            self.input_parameters["data:propulsion:propeller:efficiency"].get_val()
        )
        max_power = scalarize(
            self.input_parameters["data:propulsion: propeller:rated_power"].get_val()
        )

        # Avoid division by zero
        if efficiency == 0:
            flight_point.propeller_shaft_power = float("inf")
            flight_point.propeller_power_rate = float("inf")
        else:
            flight_point.propeller_shaft_power = thrust * true_airspeed / efficiency
            flight_point.propeller_power_rate = flight_point.propeller_shaft_power / max_power

    def compute_single_point_forward(self, flight_point: FlightPoint):
        """
        Placeholder docstring
        """
        power = flight_point.propeller_shaft_power

        # Handling each components constraints during the flight point computation might be
        # complicated, so they'll just be thrown out as constraints in the flight_points.csv file.
        # This means that models should behave properly when sightly out of their bounds
        max_power = scalarize(
            self.input_parameters["data:propulsion: propeller:rated_power"].get_val()
        )
        true_airspeed = flight_point.true_airspeed
        efficiency = scalarize(
            self.input_parameters["data:propulsion:propeller:efficiency"].get_val()
        )

        flight_point.thrust = power * efficiency / true_airspeed
        flight_point.propeller_power_rate = power / max_power
