"""
Tests for the GearboxComponent.

This module tests the functionality of the GearboxComponent including
power transmission calculations.
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

import pytest
from fastoad.model_base.flight_point import FlightPoint

from rta.models.propulsion.tests.dummy_components.gearbox import GearboxComponent


def test_gearbox_compute_single_point_backward():
    """Test single_point_backward() with a single FlightPoint."""
    # Add the input field for gearbox
    FlightPoint.add_field(name="gearbox_shaft_power", unit="W")
    gearbox = GearboxComponent()
    gearbox.input_parameters["data:propulsion:gearbox:efficiency"].value = 0.90

    fp = FlightPoint()
    fp.gearbox_shaft_power = 500000.0  # W

    gearbox.compute_single_point_backward(fp)

    # The expected results is: 500000 / 0.90 = 555555.5
    expected_power = 500000.0 / 0.90
    assert fp.TPshaft_power == pytest.approx(expected_power, rel=1e-6)


def test_gearbox_compute_single_point_forward():
    """Test single_point_forward() with a single FlightPoint."""

    FlightPoint.add_field(name="gearbox_shaft_power", unit="W")
    gearbox = GearboxComponent()
    gearbox.input_parameters["data:propulsion:gearbox:efficiency"].value = 0.90

    fp = FlightPoint()
    fp.TPshaft_power = 555555.5  # W

    gearbox.compute_single_point_forward(fp)

    # The expected results is: 550000 * 0.90 = 500000
    expected_power = 555555.5 * 0.90
    assert fp.gearbox_shaft_power == pytest.approx(expected_power, rel=1e-6)
