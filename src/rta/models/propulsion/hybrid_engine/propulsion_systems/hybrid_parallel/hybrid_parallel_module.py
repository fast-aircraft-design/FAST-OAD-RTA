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
            for idx in flight_points.index:
                fp = FlightPoint.create(flight_points.iloc[idx])
                self.compute_flight_point(fp)
                flight_points.iloc[[idx]] = pd.DataFrame([fp])
        else:
            self.compute_flight_point(flight_points)

    def compute_flight_point(self, flight_point: FlightPoint):
        """
        Placeholder docstring
        """

        if flight_point.thrust_is_regulated:
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

            # Calculate the throttle ratio, stored in the thrust rate
            flight_point.thrust_rate = throttle_ratio

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
            sfc = flight_point.fuel_flow / flight_point.thrust
            flight_point.sfc = sfc  # kg/N/s
