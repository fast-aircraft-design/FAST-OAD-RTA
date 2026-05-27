"""Base propulsion system class for use with propulsive components"""
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

from abc import ABC

from fastoad.model_base.propulsion import IPropulsion

from .component_base import AbstractPropulsiveComponent


class PropulsionSystem(IPropulsion, ABC):
    """
    Base class from which all propulsion system with standardized component should inherit

    It provides the check on input_fields units
    """

    def __init_subclass__(cls, **kwargs):
        """
        Redefine the __init__ of the child class and add the unit check at the end of __init__
        """
        super().__init_subclass__(**kwargs)

        # Get the child __init__
        child_init = cls.__init__

        def child_init_and_validate_units(self, *arg, **kwargs):
            # Call the child __init__ first to have all attributes set
            child_init(self, *arg, **kwargs)
            # Add the unit check
            self._check_units_consistency()

        # Override child __init__
        cls.__init__ = child_init_and_validate_units

    def _check_units_consistency(self):
        """
        For each propulsive component in the instance attributes list,
        run its input_field unit check
        """
        class_attribute = self.__dict__
        for attr, value in class_attribute.items():
            if isinstance(value, AbstractPropulsiveComponent):
                value._check_input_fields()
