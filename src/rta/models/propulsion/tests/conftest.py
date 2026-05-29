"""
Pytest configuration and fixtures for propulsion tests.

This module provides fixtures to ensure proper cleanup of FlightPoint fields
after tests that instantiate AbstractPropulsiveComponent subclasses.
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
import contextlib

import pytest
from fastoad.model_base.flight_point import FlightPoint


@pytest.fixture(autouse=True)
def cleanup_flight_point_fields():
    """
    Automatically clean up FlightPoint fields added during tests.

    This fixture runs before and after each test to ensure that any fields
    added to the FlightPoint class (e.g., by AbstractPropulsiveComponent
    subclasses) are removed after the test completes. This prevents field
    pollution between tests.

    Only fields that were NOT present at the start of the current test will be
    removed. This preserves fields that are legitimately needed by multiple
    tests and any shared fields added during test-module import.

    Usage:
        This fixture is automatically applied to all tests in this directory
        and subdirectories. No explicit import or usage is required.

    Example:
        def test_something():
            # Any AbstractPropulsiveComponent subclass instantiation
            # will add fields to FlightPoint, but they will be cleaned up
            # automatically after this test
            component = SomePropulsiveComponent()
            # ... test logic ...
        # FlightPoint fields are automatically cleaned up here
    """
    # Snapshot the FlightPoint fields at the start of the current test.
    initial_fields = set(FlightPoint.__dataclass_fields__.keys())

    # Run the test
    yield

    # After the test, clean up only fields that were added during this test.
    current_fields = set(FlightPoint.__dataclass_fields__.keys())
    new_fields = current_fields - initial_fields

    for field_name in new_fields:
        with contextlib.suppress(AttributeError, KeyError):
            FlightPoint.remove_field(field_name)
