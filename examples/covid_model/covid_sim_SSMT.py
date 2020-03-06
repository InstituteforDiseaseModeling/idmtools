from covid_ssmt import COVID19SSMT
from idmtools.core.platform_factory import Platform

platform = Platform('COMPS2')

wi_name = "COVID run"
wi = COVID19SSMT(item_name=wi_name, covid_abm_path=r"P:\Projects\covid_abm", run_script="run_sim.py")
wi.run(wait_on_done=True, platform=platform)
