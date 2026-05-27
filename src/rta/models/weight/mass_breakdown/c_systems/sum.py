import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel
from fastoad_cs25.models.weight.mass_breakdown.c_systems.constants import (
    SERVICE_NAVIGATION_SYSTEMS_MASS,
)
from fastoad_cs25.models.weight.mass_breakdown.constants import SERVICE_SYSTEMS_MASS

from rta.models.weight.mass_breakdown.c_systems.constants import (
    SERVICE_MASS_ATA21,
    SERVICE_MASS_ATA22,
    SERVICE_MASS_ATA23,
    SERVICE_MASS_ATA24,
    SERVICE_MASS_ATA25_SYSTEM,
    SERVICE_MASS_ATA26,
    SERVICE_MASS_ATA27,
    SERVICE_MASS_ATA29,
    SERVICE_MASS_ATA30,
    SERVICE_MASS_ATA49,
)

RegisterSubmodel.active_models[SERVICE_SYSTEMS_MASS] = "rta.submodel.weight.mass.system.legacy"


@RegisterSubmodel(SERVICE_SYSTEMS_MASS, "rta.submodel.weight.mass.system.legacy")
class SystemsWeight(om.Group):
    """
    Computes mass of systems.
    """

    def setup(self):
        self.add_subsystem(
            "ATA21", RegisterSubmodel.get_submodel(SERVICE_MASS_ATA21), promotes=["*"]
        )
        self.add_subsystem(
            "ATA22", RegisterSubmodel.get_submodel(SERVICE_MASS_ATA22), promotes=["*"]
        )
        self.add_subsystem(
            "ATA23", RegisterSubmodel.get_submodel(SERVICE_MASS_ATA23), promotes=["*"]
        )
        self.add_subsystem(
            "ATA24", RegisterSubmodel.get_submodel(SERVICE_MASS_ATA24), promotes=["*"]
        )
        self.add_subsystem(
            "ATA25",
            RegisterSubmodel.get_submodel(SERVICE_MASS_ATA25_SYSTEM),
            promotes=["*"],
        )
        self.add_subsystem(
            "ATA26", RegisterSubmodel.get_submodel(SERVICE_MASS_ATA26), promotes=["*"]
        )
        self.add_subsystem(
            "ATA27", RegisterSubmodel.get_submodel(SERVICE_MASS_ATA27), promotes=["*"]
        )
        self.add_subsystem(
            "ATA29", RegisterSubmodel.get_submodel(SERVICE_MASS_ATA29), promotes=["*"]
        )
        self.add_subsystem(
            "ATA30", RegisterSubmodel.get_submodel(SERVICE_MASS_ATA30), promotes=["*"]
        )
        self.add_subsystem(
            "ATA34",
            RegisterSubmodel.get_submodel(SERVICE_NAVIGATION_SYSTEMS_MASS),
            promotes=["*"],
        )
        self.add_subsystem(
            "ATA49", RegisterSubmodel.get_submodel(SERVICE_MASS_ATA49), promotes=["*"]
        )

        weight_sum = om.AddSubtractComp()
        weight_sum.add_equation(
            "data:weight:systems:mass",
            [
                "data:weight:systems:auxiliary_power_unit:mass",
                "data:weight:systems:electric_systems:electric_generation:mass",
                "data:weight:systems:electric_systems:electric_common_installation:mass",
                "data:weight:systems:hydraulic_systems:mass",
                "data:weight:systems:fire_protection:mass",
                "data:weight:systems:flight_furnishing:mass",
                "data:weight:systems:automatic_flight_system:mass",
                "data:weight:systems:communications:mass",
                "data:weight:systems:ECS:mass",
                "data:weight:systems:de-icing:mass",
                "data:weight:systems:navigation:mass",
                "data:weight:systems:flight_controls:mass",
            ],
            units="kg",
            desc="Mass of aircraft systems",
        )

        self.add_subsystem(
            "systems_weight_sum",
            weight_sum,
            promotes=["*"],
        )
