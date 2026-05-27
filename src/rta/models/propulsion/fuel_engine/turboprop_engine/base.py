"""Base classes for fuel-consuming propulsion models."""
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

from abc import ABC

from fastoad.model_base.flight_point import FlightPoint
from fastoad.model_base.propulsion import IPropulsion

FlightPoint.add_field("TPshaft_power", unit="W")
FlightPoint.add_field("TP_power_rate")
FlightPoint.add_field("psfc", unit="kg/W/s")
FlightPoint.add_field("TP_residual_thrust", unit="N")


class AbstractFuelPropulsion(IPropulsion, ABC):
    """
    Propulsion model that consume any fuel should inherit from this one.

    In inheritors, :meth:`compute_flight_points` is expected to define
    "sfc" and "thrust" in computed FlightPoint instances.
    """

    def get_consumed_mass(self, flight_point: FlightPoint, time_step: float) -> float:
        return time_step * flight_point.psfc * flight_point.TPshaft_power
