import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel
from fastoad_cs25.models.weight.mass_breakdown.constants import SERVICE_FURNITURE_MASS

from rta.models.weight.mass_breakdown.d_furniture.constants import (
    SERVICE_MASS_ATA25_FURNISHING,
    SERVICE_MASS_ATA33,
    SERVICE_MASS_ATA35,
    SERVICE_MASS_ATA38,
    SERVICE_MASS_ATA2510,
    SERVICE_MASS_ATA2580,
    SERVICE_MASS_ATA5345,
)

RegisterSubmodel.active_models[SERVICE_FURNITURE_MASS] = "rta.submodel.weight.mass.furniture.legacy"


@RegisterSubmodel(SERVICE_FURNITURE_MASS, "rta.submodel.weight.mass.furniture.legacy")
class FurnitureWeight(om.Group):
    """
    Computes mass of furniture.
    """

    def setup(self):
        self.add_subsystem(
            "ATA33", RegisterSubmodel.get_submodel(SERVICE_MASS_ATA33), promotes=["*"]
        )
        self.add_subsystem(
            "ATA38", RegisterSubmodel.get_submodel(SERVICE_MASS_ATA38), promotes=["*"]
        )
        self.add_subsystem(
            "ATA35", RegisterSubmodel.get_submodel(SERVICE_MASS_ATA35), promotes=["*"]
        )
        self.add_subsystem(
            "ATA25",
            RegisterSubmodel.get_submodel(SERVICE_MASS_ATA25_FURNISHING),
            promotes=["*"],
        )
        self.add_subsystem(
            "ATA2580",
            RegisterSubmodel.get_submodel(SERVICE_MASS_ATA2580),
            promotes=["*"],
        )
        self.add_subsystem(
            "ATA2510",
            RegisterSubmodel.get_submodel(SERVICE_MASS_ATA2510),
            promotes=["*"],
        )
        self.add_subsystem(
            "ATA5345_5347",
            RegisterSubmodel.get_submodel(SERVICE_MASS_ATA5345),
            promotes=["*"],
        )

        weight_sum = om.AddSubtractComp()
        weight_sum.add_equation(
            "data:weight:furniture:mass",
            [
                "data:weight:furniture:furnishing:mass",
                "data:weight:furniture:water:mass",
                "data:weight:furniture:interior_integration:mass",
                "data:weight:furniture:insulation:mass",
                "data:weight:furniture:cabin_lighting:mass",
                "data:weight:furniture:seats_crew_accommodation:mass",
                "data:weight:furniture:oxygen:mass",
            ],
            units="kg",
            desc="Mass of aircraft furniture",
        )

        self.add_subsystem(
            "furniture_weight_sum",
            weight_sum,
            promotes=["*"],
        )
