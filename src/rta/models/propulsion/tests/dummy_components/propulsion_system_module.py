"""
Propulsion system module implementation inheriting from AbstractFuelPropulsion.

This module demonstrates how to create a complete propulsion system module
by combining propeller, gearbox, and fuel flow calculations.
"""

#  This file is part of FAST : A framework for rapid Overall Aircraft Design
#  Copyright (C) 2020  ONERA & ISAE-SUPAERO
#  FAST is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import Union

import numpy as np
import pandas as pd
from fastoad.model_base.flight_point import FlightPoint

from rta.models.propulsion.fuel_engine.turboprop_engine.base import (
    AbstractFuelPropulsion,
)


class PropulsionSystemModule(AbstractFuelPropulsion):
    """
    Propulsion system module that combines propeller, gearbox, and fuel flow calculations.

    This module inherits from AbstractFuelPropulsion and orchestrates the computation
    chain: propeller -> gearbox -> fuel flow -> SFC.

    In its initialization, the module takes:
        - propeller_power_calculator: An instance of PropellerPowerCalculator
        - gearbox: An instance of GearboxComponent

    The compute_flight_points method will:
        1. Call compute_perfo of the propeller instance first
        2. Then call compute_perfo of the gearbox instance
        3. Calculate fuel flow as PSFC * TPshaft_power with PSFC = 0.250 [kg/kWh]
        4. Calculate SFC from fuel flow / thrust

    Attributes:
        propeller_power_calculator: Instance of propeller power calculator component.
        gearbox: Instance of gearbox component.
        PSFC: Specific fuel consumption constant [kg/kWh].
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
        # PSFC = 0.250 kg/kWh (specific fuel consumption constant)
        self.PSFC = 0.250  # kg/kWh

    def compute_flight_points(self, flight_points: Union[FlightPoint, pd.DataFrame]):
        """
        Compute propulsion performance for flight point(s).

        This method orchestrates the computation chain:
        1. Call propeller compute_perfo to compute gearbox_shaft_power
        2. Call gearbox compute_perfo to compute TPshaft_power
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
        # Handle both single FlightPoint and DataFrame cases
        if isinstance(flight_points, FlightPoint):
            self._compute_single_flight_point(flight_points)
        elif isinstance(flight_points, pd.DataFrame):
            for idx in flight_points.index:
                flight_point = flight_points.loc[idx]
                self._compute_single_flight_point(flight_point)
        else:
            # Assume it's a list or array of FlightPoints
            for flight_point in flight_points:
                self._compute_single_flight_point(flight_point)

    def _compute_single_flight_point(self, flight_point: FlightPoint):
        """
        Compute propulsion performance for a single flight point.

        Args:
            flight_point: A FlightPoint instance with required inputs set.
        """
        # Step 1: Call propeller compute_perfo first
        # This computes gearbox_shaft_power from thrust and true_airspeed
        self.propeller_power_calculator.compute_perfo(flight_point)

        # Step 2: Call gearbox compute_perfo
        # This computes TPshaft_power from gearbox_shaft_power
        self.gearbox.compute_perfo(flight_point)

        # Step 3: Calculate fuel flow
        # fuel_flow = PSFC * TPshaft_power
        psfc_in_kg_per_w_s = self.PSFC / (1000.0 * 3600.0)  # kg/W/s

        # Fuel flow in kg/s
        fuel_flow = psfc_in_kg_per_w_s * flight_point.TPshaft_power

        # Step 4: Calculate SFC [kg/N/s]
        sfc = fuel_flow / flight_point.thrust

        # Store results in flight point
        flight_point.psfc = psfc_in_kg_per_w_s  # kg/W/s
        flight_point.thrust = flight_point.thrust  # N (already set from propeller input)
        flight_point.sfc = sfc  # kg/N/s
