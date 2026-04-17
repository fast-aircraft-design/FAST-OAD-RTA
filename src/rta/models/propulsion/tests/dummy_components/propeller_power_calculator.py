"""
Example implementation of a propulsive component using AbstractPropulsiveComponent.

This module demonstrates how to create concrete propulsive components by
inheriting from AbstractPropulsiveComponent.
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

from dataclasses import dataclass

from fastoad.model_base.flight_point import FlightPoint
from fastoad.openmdao.variables import VariableList, Variable

from rta.models.propulsion.component_base import AbstractPropulsiveComponent


@dataclass
class PropellerPowerCalculator(AbstractPropulsiveComponent):
    """
    Example component for turboprop shaft power calculations.

    This component computes the required shaft power for a propeller
    based on thrust, velocity, and propeller efficiency.

    Inputs:
        - data:propulsion:propeller:efficiency: Propeller efficiency [1]

    FlightPoint inputs:
        - thrust: Thrust [N]
        - true_airspeed: Aircraft true airspeed [m/s]

    Outputs:
        - gearbox_shaft_power: Shaft power [W]

    Usage:
        >>> propeller = PropellerPowerCalculator()
        >>> propeller.inputs["data:propulsion:propeller:efficiency"].value(0.85)
        >>> fp = FlightPoint()
        >>> fp.thrust = 5000  # N
        >>> fp.true_airspeed = 200  # m/s
        >>> propeller.compute_perfo(fp)
        >>> print(fp.gearbox_shaft_power)
        1176470.588...
    """

    name = "PropellerPowerCalculator"

    inputs = VariableList()
    inputs.append(
        Variable(
            "data:propulsion:propeller:efficiency",
            units="unitless",
            desc="Propeller efficiency (0-1)",
        )
    )

    # Dictionary of FlightPoint fields required as input (field_name: unit)
    flightpoint_input = {
        "thrust": "N",
        "true_airspeed": "m/s",
    }

    # Dictionary of FlightPoint fields to be computed (field_name: unit)
    flightpoint_output = {
        "gearbox_shaft_power": "W",
    }

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
        efficiency = self.inputs["data:propulsion:propeller:efficiency"].get_val()

        # Avoid division by zero
        if efficiency == 0:
            flight_point.gearbox_shaft_power = float("inf")
        else:
            flight_point.gearbox_shaft_power = (thrust * true_airspeed) / efficiency

        return flight_point
