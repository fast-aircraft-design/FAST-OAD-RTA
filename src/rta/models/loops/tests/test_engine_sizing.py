from fastoad.testing import run_system
from openmdao.core.indepvarcomp import IndepVarComp
from pytest import approx

from ..compute_engine_size import ComputeEngineSize


def test_compute_engine_size():
    ivc = IndepVarComp()

    ivc.add_output("data:mission:sizing:takeoff:distance", val=950, units="m")
    ivc.add_output("data:TLAR:TOD", val=800, units="m")
    ivc.add_output("data:TLAR:TTC", val=30, units="min")
    ivc.add_output("data:TLAR:OEI_ceiling", val=8000, units="m")
    ivc.add_output("data:TLAR:cruise_mach", val=0.55)

    problem = run_system(ComputeEngineSize(), ivc)

    assert problem["data:propulsion:RTO_power"] == approx(4.301e6, rel=1e-3)
    assert problem["data:propulsion:design_thermal_power"] == approx(5.247e6, rel=1e-3)
    assert problem["data:propulsion:propeller:max_power"] == approx(4.705e6, rel=1e-3)
