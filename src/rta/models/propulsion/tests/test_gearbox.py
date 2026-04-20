"""
Tests for the GearboxComponent.

This module tests the functionality of the GearboxComponent including
power transmission calculations.
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

import pytest

from fastoad.model_base.flight_point import FlightPoint

from rta.models.propulsion.tests.dummy_components.gearbox import GearboxComponent


def test_gearbox_compute_perfo_single_flight_point():
    """Test compute_perfo() with a single FlightPoint."""
    try:
        gearbox = GearboxComponent()
        gearbox.input_parameters["data:propulsion:gearbox:efficiency"].value = 0.90

        fp = FlightPoint()
        fp.gearbox_shaft_power = 500000.0  # W

        gearbox.compute_perfo(fp)

        # Expected: 500000 / 0.90 = 550000
        expected_power = 500000.0 / 0.90
        assert fp.TPshaft_power == pytest.approx(expected_power, rel=1e-6)

    finally:
        for field, val in GearboxComponent.output_fields.items():
            FlightPoint.remove_field(field)


def test_gearbox_compute_perfo_list_of_flight_points():
    """Test compute_perfo() with a list of FlightPoints."""
    try:
        FlightPoint.add_field(name="gearbox_shaft_power", unit="W")
        gearbox = GearboxComponent()
        gearbox.input_parameters["data:propulsion:gearbox:efficiency"].value = 0.95

        fp1 = FlightPoint()
        fp1.gearbox_shaft_power = 1000000.0

        fp2 = FlightPoint()
        fp2.gearbox_shaft_power = 2000000.0

        gearbox.compute_perfo([fp1, fp2])

        # First result: 1000000 / 0.95
        expected_power1 = 1000000.0 / 0.95
        assert fp1.TPshaft_power == pytest.approx(expected_power1, rel=1e-6)

        # Second result: 2000000 / 0.95
        expected_power2 = 2000000.0 / 0.95
        assert fp2.TPshaft_power == pytest.approx(expected_power2, rel=1e-6)
    finally:
        for field, val in GearboxComponent.output_fields.items():
            FlightPoint.remove_field(field)
