"""
Gearbox component implementation using AbstractPropulsiveComponent.

This module provides a gearbox component that computes output shaft power
based on input power and gearbox efficiency.
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
from fastoad.model_base.flight_point import FlightPoint
from fastoad.openmdao.variables import VariableList, Variable

from rta.models.propulsion.component_base import AbstractPropulsiveComponent


class GearboxComponent(AbstractPropulsiveComponent):
    """
    Component for gearbox power transmission calculations.

    This component computes the output shaft power from a gearbox based on
    input power and gearbox efficiency.

    input_parameters:
        - data:propulsion:gearbox:efficiency: Gearbox efficiency [1]

    FlightPoint input fields:
        - gearbox_shaft_power: Input shaft power [W]

    FlightPoint output fields:
        - TPshaft_power: Output shaft power [W]

    Usage:
        >>> gearbox = GearboxComponent()
        >>> fp = FlightPoint()
        >>> fp.gearbox_shaft_power = 1000000  # W
        >>> gearbox.input_parameters["data:propulsion:gearbox:efficiency"].value = 0.95
        >>> gearbox.compute_perfo(fp)
        >>> print(fp.TPshaft_power)
        950000.0
    """

    name = "GearboxComponent"

    input_parameters = VariableList(
        [
            Variable(
                "data:propulsion:gearbox:efficiency",
                val=np.nan,
                units="unitless",
                desc="Gearbox efficiency (0-1)",
            )
        ]
    )

    # Dictionary of FlightPoint fields required as input (field_name: unit)
    input_fields = {
        "gearbox_shaft_power": "W",
    }

    # Dictionary of FlightPoint fields to be computed (field_name: unit)
    output_fields = {
        "TPshaft_power": "W",
    }

    def compute_single_point(self, flight_point: FlightPoint):
        """
        Compute output shaft power for a single flight point.

        Output Power = Input Power * Efficiency

        Args:
            flight_point: FlightPoint with gearbox_shaft_power and efficiency set.

        Returns:
            FlightPoint with TPshaft_power computed.
        """
        input_power = flight_point.gearbox_shaft_power
        efficiency = self.input_parameters["data:propulsion:gearbox:efficiency"].get_val()

        # Compute output power
        flight_point.TPshaft_power = input_power / efficiency
