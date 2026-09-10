"""
Propulsion system module implementation inheriting from AbstractFuelPropulsion.

This module demonstrates how to create a complete propulsion system module
by combining propeller, gearbox, and fuel flow calculations.
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
from fastoad.model_base.flight_point import FlightPoint

from rta.models.propulsion.propulsion_system_base import PropulsionSystem


class PropulsionSystemModule(PropulsionSystem):
    """
    Propulsion system module that combines propeller, gearbox, and fuel flow calculations.

    This module inherits from AbstractFuelPropulsion and orchestrates the computation
    chain: propeller -> gearbox -> fuel flow -> SFC.

    In its initialization, the module takes:
        - propeller: An instance of PropellerComponent
        - gearbox: An instance of GearboxComponent

    The compute_flight_points method will:
        1. Call compute_performances of the propeller instance first
        2. Then call compute_performances of the gearbox instance
        3. Calculate fuel flow as PSFC * TPshaft_power with PSFC = 0.250 [kg/kWh]
        4. Calculate SFC from fuel flow / thrust

    Attributes:
        propeller: Instance of propeller component.
        gearbox: Instance of gearbox component.
    """

    def __init__(
        self,
        propeller,
        gearbox,
    ):
        """
        Initialize the propulsion system module.

        Args:
            propeller: An instance of PropellerComponent.
            gearbox: An instance of GearboxComponent.
        """
        self.propeller = propeller
        self.gearbox = gearbox
        self.PSFC = 0.250  # kg/kWh
        self.TPshaft_power_max = 20  # MW

    def get_consumed_mass(self, flight_point: FlightPoint, time_step: float) -> float:
        """Definition is mandatory but it is not used in this exemple"""
        pass

    def compute_flight_points(self, flight_points: FlightPoint | pd.DataFrame):
        """
        Compute the performance of the propulsion system for given flight point(s).

        This method handles both single FlightPoint instances and lists of
        FlightPoint instances. It delegates the actual computation to the
        compute_flight_point() method.

        Args:
            flight_points: A FlightPoint or list of FlightPoint to compute
                          performance for.
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
        Compute propulsion performance for a single flight point.

        This method orchestrates the computation chain.
        In backward mode
            1. Call propeller compute_single_point_backward to compute gearbox_shaft_power
            2. Call gearbox compute_single_point_backward to compute TPshaft_power
            3. Calculate fuel flow as PSFC * TPshaft_power
            4. Calculate SFC as fuel_flow / thrust
        In forward mode
            1. Calculate the gas turbine power at throttle ratio
            2. Calculate fuel flow as PSFC * TPshaft_power
            3. Calculate SFC as fuel_flow / thrust
            4. Call gearbox compute_single_point_forward to compute gearbox_shaft_power
            5. Call propeller compute_single_point_forward to compute thrust

        Args:
            flight_point: A FlightPoint instance.

        Returns:
            The same FlightPoint with computed outputs filled in:
                - psfc: Specific fuel consumption [kg/W/s]
                - thrust: Thrust [N] (from input flight point)
                - sfc: Specific fuel consumption [kg/N/s]
        """

        if flight_point.thrust_is_regulated:
            # Step 1: Call propeller compute_single_point_backward first
            # This computes gearbox_shaft_power from thrust and true_airspeed
            self.propeller.compute_single_point_backward(flight_point)

            # Step 2: Call gearbox compute_single_point_backward
            # This computes TPshaft_power from gearbox_shaft_power
            self.gearbox.compute_single_point_backward(flight_point)

            # Step 3: Calculate the fuel flow as: fuel_flow = PSFC * TPshaft_power
            psfc_in_kg_per_w_s = self.PSFC / (1000.0 * 3600.0)  # kg/W/s

            # Fuel flow in kg/s
            fuel_flow = psfc_in_kg_per_w_s * flight_point.TPshaft_power

            # Step 4: Calculate SFC [kg/N/s]
            sfc = fuel_flow / flight_point.thrust

            # Store results in flight point
            flight_point.psfc = psfc_in_kg_per_w_s  # kg/W/s
            flight_point.sfc = sfc  # kg/N/s

            # Step 5: Calculate the throttle ratio, stored in the thrust rate
            flight_point.thrust_rate = flight_point.TPshaft_power / (self.TPshaft_power_max * 1e6)

        else:
            # Step 1: Get the power available on the gas turbine first.
            # Thrust rate acts here as a throttle ratio.
            flight_point.TPshaft_power = self.TPshaft_power_max * 1e6 * flight_point.thrust_rate

            # Step 2: Calculate the fuel flow as: fuel_flow = PSFC * TPshaft_power
            psfc_in_kg_per_w_s = self.PSFC / (1000.0 * 3600.0)  # kg/W/s

            # Fuel flow in kg/s
            fuel_flow = psfc_in_kg_per_w_s * flight_point.TPshaft_power

            # Step 3: Call the gearbox compute_single_point_forward
            # This computes gearbox_shaft_power from TPshaft_power
            self.gearbox.compute_single_point_forward(flight_point)

            # Step 4: Finally, call the propeller compute_single_point_forward
            # This computes thrust from gearbox_shaft_power and velocity
            self.propeller.compute_single_point_forward(flight_point)

            # Step 5: Calculate SFC [kg/N/s]
            sfc = fuel_flow / flight_point.thrust

            # Store results in flight point
            flight_point.psfc = psfc_in_kg_per_w_s  # kg/W/s
            flight_point.sfc = sfc  # kg/N/s
