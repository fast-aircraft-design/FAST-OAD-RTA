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
        - propeller_power_calculator: An instance of PropellerPowerCalculator
        - gearbox: An instance of GearboxComponent

    The compute_flight_points method will:
        1. Call compute_performances of the propeller instance first
        2. Then call compute_performances of the gearbox instance
        3. Calculate fuel flow as PSFC * TPshaft_power with PSFC = 0.250 [kg/kWh]
        4. Calculate SFC from fuel flow / thrust

    Attributes:
        propeller_power_calculator: Instance of propeller power calculator component.
        gearbox: Instance of gearbox component.
    """

    def __init__(
        self,
        propeller_power_calculator,
        gearbox,
    ):
        """
        Initialize the propulsion system module.

        Args:
            propeller_power_calculator: An instance of PropellerPowerCalculator.
            gearbox: An instance of GearboxComponent.
        """
        self.propeller_power_calculator = propeller_power_calculator
        self.gearbox = gearbox
        self.PSFC = 0.250  # kg/kWh

    def get_consumed_mass(self, flight_point: FlightPoint, time_step: float) -> float:
        """Definition is mandatory but it is not used in this exemple"""
        return 0.0

    def compute_flight_points(self, flight_points: FlightPoint | pd.DataFrame):
        """
        Compute propulsion performance for flight point(s).

        This method orchestrates the computation chain:
        1. Call propeller compute_performances to compute gearbox_shaft_power
        2. Call gearbox compute_performances to compute TPshaft_power
        3. Calculate fuel flow as PSFC * TPshaft_power
        4. Calculate SFC as fuel_flow / thrust

        Args:
            flight_points: A FlightPoint instance or DataFrame of flight points.

        Returns:
            The same FlightPoint(s) with computed outputs filled in:
                - psfc: Specific fuel consumption [kg/W/s]
                - thrust: Thrust [N] (from input flight point)
                - sfc: Specific fuel consumption [kg/N/s]
        """

        # Step 1: Call propeller compute_perfo first
        # This computes gearbox_shaft_power from thrust and true_airspeed
        self.propeller_power_calculator.compute_performances(flight_points)

        # Step 2: Call gearbox compute_perfo
        # This computes TPshaft_power from gearbox_shaft_power
        self.gearbox.compute_performances(flight_points)

        # Step 3: Calculate the fuel flow as: fuel_flow = PSFC * TPshaft_power
        psfc_in_kg_per_w_s = self.PSFC / (1000.0 * 3600.0)  # kg/W/s

        # Fuel flow in kg/s
        fuel_flow = psfc_in_kg_per_w_s * flight_points.TPshaft_power

        # Step 4: Calculate SFC [kg/N/s]
        sfc = fuel_flow / flight_points.thrust

        # Store results in flight point
        flight_points.psfc = psfc_in_kg_per_w_s  # kg/W/s
        flight_points.sfc = sfc  # kg/N/s
