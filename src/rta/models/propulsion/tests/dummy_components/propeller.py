"""
Example implementation of a propulsive component using AbstractPropulsiveComponent.

This module demonstrates how to create concrete propulsive components by
inheriting from AbstractPropulsiveComponent.
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
        )
    ]
)

INPUT_FILEDS = {
    "thrust": _FieldDescriptor(unit="N"),
    "true_airspeed": _FieldDescriptor(unit="m/s"),
}

OUTPUT_FIELDS = {
    "gearbox_shaft_power": _FieldDescriptor(unit="W", is_cumulative=True),
}


@dataclass
class PropellerComponent(AbstractPropulsiveComponent):
    """
    Example component for turboprop shaft power calculations.

    This component computes the required shaft power for a propeller
    based on thrust, velocity, and propeller efficiency.

    input_parameters:
        - data:propulsion:propeller:efficiency: Propeller efficiency [0-1]

    FlightPoint input fields:
        - thrust: Thrust [N]
        - true_airspeed: Aircraft true airspeed [m/s]

    FlightPoint output fields:
        - gearbox_shaft_power: Shaft power [W]

    Usage:
        >>> propeller = PropellerComponent()
        >>> propeller.input_parameters["data:propulsion:propeller:efficiency"].value = 0.85
        >>> fp = FlightPoint()
        >>> fp.thrust = 5000  # N
        >>> fp.true_airspeed = 200  # m/s
        >>> propeller.compute_performances(fp)
        >>> print(fp.gearbox_shaft_power)
        1176470.588...
    """

    name = "PropellerPowerCalculator"

    _input_parameters: ClassVar[list] = INPUT_PARAMETERS

    # Dictionary of FlightPoint fields required as input (field_name: unit)
    _input_fields: ClassVar[dict] = INPUT_FILEDS

    # Dictionary of FlightPoint fields to be computed (field_name: unit)
    _output_fields: ClassVar[dict] = OUTPUT_FIELDS

    def compute_single_point(self, flight_point: FlightPoint) -> FlightPoint:
        """
        Compute shaft power for a single flight point.

        Power = (Thrust * Velocity) / Efficiency

        Args:
            flight_point: FlightPoint with thrust, velocity, and efficiency set.

        Returns:
            FlightPoint with gearbox_shaft_power computed.
        """
        thrust = flight_point.thrust
        true_airspeed = flight_point.true_airspeed
        efficiency = self.input_parameters["data:propulsion:propeller:efficiency"].get_val()

        # Avoid division by zero
        if efficiency == 0:
            flight_point.gearbox_shaft_power = float("inf")
        else:
            flight_point.gearbox_shaft_power = thrust * true_airspeed / efficiency

        return flight_point
