"""
Placeholder hybrid parallel module
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

import pandas as pd
from fastoad._utils.arrays import scalarize
from fastoad.model_base.flight_point import FlightPoint

from rta.models.propulsion.propulsion_system_base import PropulsionSystem

from ...exceptions import RTAInconsistentInputParametersError


class HybridParallelModule(PropulsionSystem):
    """
    Placeholder docstring
    """

    def __init__(
        self,
        propeller,
        gearbox_controller,
        gearbox,
        gas_turbine,
        electric_motor,
        inverter,
        battery,
    ):
        """
        Placeholder docstring
        """
        self.propeller = propeller
        self.gearbox_controller = gearbox_controller
        self.gearbox = gearbox
        self.gas_turbine = gas_turbine
        self.electric_motor = electric_motor
        self.inverter = inverter
        self.battery = battery

    def get_consumed_mass(self, flight_point: FlightPoint, time_step: float) -> float:
        return time_step * flight_point.psfc * flight_point.thermal_shaft_power

    def compute_flight_points(self, flight_points: FlightPoint | pd.DataFrame):
        """
        Placeholder docstring
        """

        if isinstance(flight_points, pd.DataFrame):
            # Default inefficient but functional way of handling dataframe.
            # User should redefine the method if relying heavily on dataframe,
            # which is not the default case
            for idx in range(len(flight_points)):
                fp = FlightPoint.create(flight_points.iloc[idx])
                self.compute_flight_point(fp)
                flight_points.iloc[[idx]] = pd.DataFrame([fp])
        else:
            self.compute_flight_point(flight_points)

    def compute_flight_point(self, flight_point: FlightPoint):
        """
        Placeholder docstring
        """

        thrust_is_regulated = self._check_thrust_inputs(
            flight_point.thrust_is_regulated, flight_point.thrust_rate, flight_point.thrust
        )

        if thrust_is_regulated:
            self.propeller.compute_single_point_backward(flight_point)

            # Here the gearbox acts as a regulator between sources so this is where a control
            # strategy should be implemented. Using a fix ratio for now
            self.gearbox_controller.compute_single_point_backward(flight_point)

            self.gearbox.compute_single_point_backward(flight_point)
            self.gas_turbine.compute_single_point_backward(flight_point)
            self.electric_motor.compute_single_point_backward(flight_point)
            self.inverter.compute_single_point_backward(flight_point)
            self.battery.compute_single_point_backward(flight_point)

            # These fields should be populated at this point
            # Not an ideal way to do it but the implementation will likely have to be powertrain
            # dependent
            throttle_ratio = (flight_point.thermal_shaft_power + flight_point.electric_dc_power) / (
                scalarize(
                    self.gas_turbine.input_parameters[
                        "data:propulsion:gas_turbine:rto_power"
                    ].get_val()
                )
                + scalarize(
                    self.battery.input_parameters["data:propulsion:battery:rated_power"].get_val()
                )
            )

            # Calculate the throttle ratio, stored in the thrust rate and the SFC in kg/N/s
            flight_point.thrust_rate = throttle_ratio
            flight_point.sfc = flight_point.fuel_flow / flight_point.thrust

        else:
            # First step is to interpret the thrust rate as power ratio on sources. Depend on a
            # control logic which will be architecture dependent
            flight_point.gas_turbine_power_rate = flight_point.thrust_rate
            flight_point.battery_power_rate = flight_point.thrust_rate

            self.battery.compute_single_point_forward(flight_point)
            self.inverter.compute_single_point_forward(flight_point)
            self.electric_motor.compute_single_point_forward(flight_point)
            self.gas_turbine.compute_single_point_forward(flight_point)

            self.gearbox.compute_single_point_forward(flight_point)
            # In backward mode, the controller does nothing.

            self.propeller.compute_single_point_forward(flight_point)

            # Step 5: Calculate SFC [kg/N/s]
            flight_point.sfc = flight_point.fuel_flow / flight_point.thrust

    @staticmethod
    def _check_thrust_inputs(thrust_is_regulated: float, thrust_rate: float, thrust: float) -> bool:
        """
        This method checks that the inputs are consistent. Unlike the rubber engine's version of
        this method, it does not cast to a specific shape and only applies to floats. Returns the
        value of thrust is regulated or raises an error in the case of an inconsistent behaviour

        :param thrust_is_regulated: flight point's thrust_is_regulated field
        :param thrust_rate: flight point's thrust_rate field
        :param thrust: flight point's thrust field
        :return: the corrected value of thrust_is_regulated, thrust_rate and thrust
        """

        thrust_is_regulated = bool(round(thrust_is_regulated, 0))

        # If thrust_is_regulated is not specified infer its value from the other field,
        # prioritizing the use of the thrust_rate
        if thrust_is_regulated is None:
            if thrust_rate is not None:
                return False
            if thrust is not None:
                return True
            raise RTAInconsistentInputParametersError(
                "When thrust_is_regulated is None, either thrust_rate or thrust should be provided."
            )

        # If it is specified, check that the required input is provided
        if thrust_is_regulated:
            if thrust is None:
                raise RTAInconsistentInputParametersError(
                    "When thrust_is_regulated is True, thrust should be provided."
                )
        elif thrust_rate is None:
            raise RTAInconsistentInputParametersError(
                "When thrust_is_regulated is False, thrust_rate should be provided."
            )

        return thrust_is_regulated
