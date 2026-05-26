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
