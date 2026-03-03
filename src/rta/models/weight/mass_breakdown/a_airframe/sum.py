import openmdao.api as om
from fastoad.module_management.service_registry import RegisterSubmodel
from fastoad_cs25.models.weight.mass_breakdown.a_airframe.constants import (
    SERVICE_EMPENNAGE_MASS,
    SERVICE_FUSELAGE_MASS,
    SERVICE_LANDING_GEARS_MASS,
    SERVICE_WING_MASS,
)
from fastoad_cs25.models.weight.mass_breakdown.constants import (
    SERVICE_AIRFRAME_MASS,
)

from rta.models.weight.mass_breakdown.a_airframe.constants import SERVICE_NACELLE_MASS

RegisterSubmodel.active_models[SERVICE_AIRFRAME_MASS] = "rta.submodel.weight.mass.airframe.legacy"


@RegisterSubmodel(SERVICE_AIRFRAME_MASS, "rta.submodel.weight.mass.airframe.legacy")
class AirframeWeight(om.Group):
    """
    Computes mass of airframe.
    """

    def setup(self):
        # Airframe
        self.add_subsystem(
            "ATA57", RegisterSubmodel.get_submodel(SERVICE_WING_MASS), promotes=["*"]
        )
        self.add_subsystem(
            "ATA53",
            RegisterSubmodel.get_submodel(SERVICE_FUSELAGE_MASS),
            promotes=["*"],
        )
        self.add_subsystem(
            "ATA55",
            RegisterSubmodel.get_submodel(SERVICE_EMPENNAGE_MASS),
            promotes=["*"],
        )
        self.add_subsystem(
            "ATA32",
            RegisterSubmodel.get_submodel(SERVICE_LANDING_GEARS_MASS),
            promotes=["*"],
        )
        self.add_subsystem(
            "ATA54", RegisterSubmodel.get_submodel(SERVICE_NACELLE_MASS), promotes=["*"]
        )

        weight_sum = om.AddSubtractComp()
        weight_sum.add_equation(
            "data:weight:airframe:mass",
            [
                "data:weight:airframe:wing:mass",
                "data:weight:airframe:fuselage:mass",
                "data:weight:airframe:horizontal_tail:mass",
                "data:weight:airframe:vertical_tail:mass",
                "data:weight:airframe:landing_gear:main:mass",
                "data:weight:airframe:landing_gear:front:mass",
                "data:weight:airframe:nacelle:mass",
            ],
            units="kg",
            desc="Mass of airframe",
        )

        self.add_subsystem(
            "airframe_weight_sum",
            weight_sum,
            promotes=["*"],
        )
