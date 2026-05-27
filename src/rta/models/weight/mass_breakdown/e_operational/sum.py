import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel

from rta.models.weight.mass_breakdown.constants import SERVICE_OPERATIONAL_MASS

from .operational_equipment_weight import OperationalEquipmentsWeight
from .operational_items_weight import OperationalItemsWeight


@RegisterSubmodel(SERVICE_OPERATIONAL_MASS, "rta.submodel.weight.mass.operational.legacy")
class OperationalWeight(om.Group):
    """
    Computes mass of operational items and equipments.
    """

    def setup(self):
        self.add_subsystem("Op_items", OperationalItemsWeight(), promotes=["*"])
        self.add_subsystem("Op_equipment", OperationalEquipmentsWeight(), promotes=["*"])

        weight_sum = om.AddSubtractComp()
        weight_sum.add_equation(
            "data:weight:operational:mass",
            [
                "data:weight:operational:items:passenger_seats:mass",
                "data:weight:operational:items:unusable_fuel:mass",
                "data:weight:operational:items:documents_toolkit:mass",
                "data:weight:operational:items:galley_structure:mass",
                "data:weight:operational:equipment:others:mass",
                "data:weight:operational:equipment:crew:mass",
            ],
            units="kg",
            desc="Mass of aircraft operational items and equipments",
        )

        self.add_subsystem(
            "operational_weight_sum",
            weight_sum,
            promotes=["*"],
        )
