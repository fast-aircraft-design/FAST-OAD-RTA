"""
Abstract base classes for propulsive components in RTA.

This module provides a standardized interface for implementing propulsive
components that can be used in aircraft performance calculations.
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

import warnings
from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass, field
from typing import ClassVar, Union

from fastoad.model_base.flight_point import FlightPoint
from fastoad.openmdao.variables import Variable, VariableList


@dataclass
class AbstractPropulsiveComponent(ABC):
    """
    Abstract base class for propulsive components in RTA.

    All propulsive components should inherit from this class to ensure
    standardized interface for performance computation.

    Subclasses must:
        1. Define class-level `name` as a string identifying the component
        2. Define class-level `inputs` as VariableList instance
        3. Define class-level `flightpoint_input` and `flightpoint_output` as dictionaries
           mapping FlightPoint field names to their units
        4. Implement the `compute_single_point()` method with their specific logic

    Attributes:
        name: Class-level string identifying the component name (used in error messages).
        inputs: Class-level VariableList declaring input variables for the component.
        flightpoint_input: Dictionary of FlightPoint field names required as input with their units.
        flightpoint_output: Dictionary of FlightPoint field names to be computed with their units.
    """

    # Class-level name for the component (must be defined by subclasses)
    name: ClassVar[str] = "UnnamedComponent"

    # Instance-level copy of class-level VariableLists (for potential per-instance modifications)
    _inputs: VariableList = field(default=VariableList, init=False, repr=False)
    _flightpoint_input: dict = field(default=None, init=False, repr=False)
    _flightpoint_output: dict = field(default=None, init=False, repr=False)

    def __post_init__(self):
        """
        Initialize the component and automatically expand FlightPoint with output fields.
        """
        # Copy class-level VariableLists to instance level using deepcopy
        # self._inputs = deepcopy(self.inputs)
        # self._flightpoint_input = dict(self.flightpoint_input)
        # self._flightpoint_output = dict(self.flightpoint_output)

        # Automatically expand FlightPoint class with output fields
        self._expand_flight_point()

    @property
    def inputs(self) -> VariableList:
        """
        Get the input VariableList.

        Returns:
            The input VariableList for this component.
        """
        return self._inputs

    @inputs.setter
    def inputs(self, value: VariableList):
        """Set the input VariableList."""
        self._inputs = value

    @property
    def flightpoint_input(self) -> dict:
        """
        Get the dictionary of input FlightPoint fields.

        Returns:
            Dictionary mapping FlightPoint field names to their units.
        """
        return self._flightpoint_input

    @property
    def flightpoint_output(self) -> dict:
        """
        Get the dictionary of output FlightPoint fields.

        Returns:
            Dictionary mapping FlightPoint field names to their units.
        """
        return self._flightpoint_output

    def _expand_flight_point(self) -> None:
        """
        Automatically expand FlightPoint class with component's output fields.

        This method is called automatically during initialization. It adds the
        necessary fields to the FlightPoint class. If a field already exists,
        a warning is issued to alert about potential redundant declarations.

        The method uses FlightPoint.add_field() to dynamically add fields for
        each output variable declared in the flightpoint_output dictionary.
        """
        for field_name, unit in self.flightpoint_output.items():
            if hasattr(FlightPoint, field_name):
                warnings.warn(
                    f"Component '{self.name}' attempts to expand FlightPoint with "
                    f"field '{field_name}' but it is already present. "
                    f"Check redondant declarations."
                )
            else:
                FlightPoint.add_field(field_name, unit=unit)

    def _check_flightpoint_input_fields(self) -> None:
        """
        Check that all fields declared in flightpoint_input are part of the FlightPoint class.

        This method should be called inside compute_perfo() before processing flight points.
        It validates that all required input fields exist in the FlightPoint class.

        Raises:
            ValueError: If one or more required input fields are missing from the FlightPoint class.
        """
        missing_fields = []
        for field_name in self.flightpoint_input.keys():
            if not hasattr(FlightPoint, field_name):
                missing_fields.append(field_name)

        if missing_fields:
            raise ValueError(
                f"Component '{self.name}': The following required input fields are missing "
                f"from the FlightPoint class: {', '.join(missing_fields)}. "
                f"Please ensure these fields are properly defined in the FlightPoint class "
                f"or remove them from the flightpoint_input dictionary."
            )

    def compute_perfo(self, flight_point: Union[FlightPoint, list[FlightPoint]]):
        """
        Compute the performance of the component for given flight point(s).

        This method handles both single FlightPoint instances and lists of
        FlightPoint instances. It delegates the actual computation to the
        compute_single_point() method which must be implemented by subclasses.

        Args:
            flight_point: A FlightPoint or list of FlightPoint to compute
                          performance for.

        Returns:
            The same FlightPoint(s) with computed outputs filled in.

        Raises:
            NotImplementedError: If the subclass has not implemented
                                 compute_single_point().
        """
        # Check that all required input fields exist in FlightPoint class
        self._check_flightpoint_input_fields()

        if isinstance(flight_point, list):
            for fp in flight_point:
                self.compute_single_point(fp)
        else:
            self.compute_single_point(flight_point)

    @abstractmethod
    def compute_single_point(self, flight_point: FlightPoint) -> FlightPoint:
        """
        Compute performance for a single flight point.

        Subclasses must override this method with their specific calculations.
        This method receives a FlightPoint with input values populated and
        must return the same FlightPoint with output values computed and filled in.

        Args:
            flight_point: A single FlightPoint instance with input values set.

        Returns:
            The FlightPoint with computed output values.

        Raises:
            NotImplementedError: If the subclass has not implemented this method.
        """
        raise NotImplementedError(
            f"Subclass {self.__class__.__name__} must implement compute_single_point()"
        )
