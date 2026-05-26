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
from dataclasses import dataclass

import pandas as pd
from openmdao.vectors.default_vector import DefaultVector
from openmdao.core.component import Component
from typing import ClassVar, Union
from copy import deepcopy

from fastoad.model_base.flight_point import FlightPoint, _FieldDescriptor
from fastoad.openmdao.variables import VariableList


@dataclass
class AbstractPropulsiveComponent(ABC):
    """
    Abstract base class for propulsive components in RTA.

    All propulsive components should inherit from this class to ensure
    standardized interface for performance computation.

    Subclasses must:
        1. Define class-level `name` as a string identifying the component
        2. Define class-level `_input_parameters` as VariableList instance with default variables names
        3. Define class-level `_input_fields` and `_output_fields` as dictionaries
           mapping FlightPoint field names to a FieldDescriptor (units and is_cumulative) with default field names
        4. Implement the `compute_single_point()` method with their specific logic

    Attributes:
        name: Class-level string identifying the component name (used in error messages).
        input_parameters: Class-level VariableList declaring input parameters for the component.
        input_fields: Dictionary of FlightPoint field names required as input with their units.
        output_fields: Dictionary of FlightPoint field names to be computed with their units.
    """

    # Name of the component
    name: ClassVar[str] = None

    # Input parameters, all parameters defining the components and required for calculation of FlightPoint
    input_parameters: VariableList = None

    # Inputs fields that should be present in the FlightPoint class to compute component performances
    input_fields: dict = None

    # Output fields that will be added to the FlightPoint class and computed by the components
    output_fields: dict = None

    # Subclasses must declare these with default variable and field names
    _input_parameters: ClassVar[VariableList] = None
    _input_fields: ClassVar[dict] = None
    _output_fields: ClassVar[dict] = None

    def __init_subclass__(cls, **kwargs):
        """
        This function is called when initializing subclasses.
        It makes sure that the child class has declared the following
        default attributes:
        _input_parameters, _input_fields and _output_fields.
        """
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "_input_parameters"):
            raise ValueError(f"The classe {cls.__name__} must define _input_parameters")
        if not hasattr(cls, "_input_fields"):
            raise ValueError(f"The classe {cls.__name__} must define _input_fields")
        if not hasattr(cls, "_output_fields"):
            raise ValueError(f"The classe {cls.__name__} must define _output_fields")

    def __post_init__(self):
        """
        Initialize the component and automatically expand FlightPoint with output fields.

        We use default attributes defined by child class, unless new attributes
        are provided at instantiation.
        """

        if self.input_parameters is None:
            self.input_parameters = deepcopy(self._input_parameters)

        if self.input_fields is None:
            self.input_fields = deepcopy(self._input_fields)

        if self.output_fields is None:
            self.output_fields = deepcopy(self._output_fields)

        # Automatically expand FlightPoint class with output fields
        self._expand_flight_point()

    @staticmethod
    def _check_fields_definition(fields: dict):
        """Raises a TypeError if the fields in dictionary are not declared using _FieldDescriptor"""
        bad_fields = []
        for field_name, metadata in fields.items():
            if not isinstance(metadata, _FieldDescriptor):
                bad_fields.append(field_name)

        if bad_fields:
            raise TypeError(
                f"The fields {', '.join(bad_fields)} must be declared using _FieldDescriptor"
            )

    def _expand_flight_point(self) -> None:
        """
        Automatically expand FlightPoint class with component's output fields.

        This method is called automatically during instantiation. It adds the
        necessary fields to the FlightPoint class. If a field already exists,
        a warning is issued to alert about potential redundant declarations.

        The method uses FlightPoint.add_field() to dynamically add fields for
        each output variable declared in the output_fields dictionary.
        """
        for field_name, metadata in self.output_fields.items():
            if hasattr(FlightPoint, field_name):
                warnings.warn(
                    f"Component '{self.name}' attempts to expand FlightPoint with "
                    f"field '{field_name}' but it is already present. "
                    f"Check for redundant declarations."
                )
            else:
                FlightPoint.add_field(
                    field_name,
                    unit=metadata.unit,
                    is_cumulative=metadata.is_cumulative,
                    integrates_from=metadata.integrates_from,
                )

    def _check_input_fields(self) -> None:
        """
        Check that all fields declared in input_fields are part of the FlightPoint class.
        Raises:
            ValueError: If one or more required input fields are missing from the FlightPoint class.
        """
        missing_fields = []
        fields = []
        unit_inconsistency = []
        for field_name in self.input_fields.keys():
            if not hasattr(FlightPoint, field_name):
                missing_fields.append(field_name)
            elif FlightPoint.get_unit(field_name) != self.input_fields[field_name].unit:
                fields.append(field_name)
                unit_inconsistency.append(self.input_fields[field_name].unit)

        if missing_fields:
            raise ValueError(
                f"Component '{self.name}': The following required input fields are missing "
                f"from the FlightPoint class: {', '.join(missing_fields)}. "
                f"Please ensure these fields are properly defined in the FlightPoint class "
                f"or remove them from the input_fields dictionary."
            )
        elif unit_inconsistency:
            raise ValueError(
                f"Component '{self.name}': The following input fields: {', '.join(fields)} asked for the following units "
                f": {', '.join(unit_inconsistency)} which are inconsistent with the units already declared in FlightPoint"
                f"Please ensure units consistency between input and output fields."
            )

    def compute_performances(self, flight_point: Union[FlightPoint, pd.DataFrame]):
        """
        Compute the performance of the component for given flight point(s).

        This method handles both single FlightPoint instances and lists of
        FlightPoint instances. It delegates the actual computation to the
        compute_single_point() method which must be implemented by subclasses.

        Args:
            flight_point: A FlightPoint or list of FlightPoint to compute
                          performance for.


        Raises:
            NotImplementedError: If the subclass has not implemented
                                 compute_single_point().
        """

        if isinstance(flight_point, pd.DataFrame):
            # Default inefficient but functional way of handling dataframe.
            # User should redefine the method if relying heavily on dataframe, which is not the default case
            for idx in flight_point.index:
                fp = FlightPoint.create(flight_point.iloc[idx])
                self.compute_single_point(fp)
                flight_point.iloc[[idx]] = pd.DataFrame([fp])
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

    def update_input_parameters(self, inputs: DefaultVector):
        """Update the input_parameters list from openmdao vector"""

        for name in self.input_parameters.names():
            self.input_parameters[name].value = inputs[name]

    def declare_openmdao_inputs(self, component: Component):
        """
        For use with openmdao wrapper, declares the input parameters as openmdao inputs with units check
        """
        faulty_units = []
        for var in self._input_parameters:
            if var not in component.list_inputs():
                component.add_input(var.name, var.value, units=var.units)
            elif var.units != component._get_var_meta(var, "units"):
                faulty_units.append(var)

        if faulty_units:
            raise ValueError(
                f"The variables {', '.join(faulty_units)} declared in component '{self.name}' has"
                f"already been added as openmdao input with different units,"
                f"check units consistency"
            )
