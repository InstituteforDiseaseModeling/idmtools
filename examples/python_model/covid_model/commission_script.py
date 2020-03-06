from covid_ssmt import COVID19SSMT
from idmtools.core.platform_factory import Platform


# Create a platform to run the workitem
platform = Platform('COMPS2')

# Create a COVIDSSMT worker
wi = COVID19SSMT(item_name="COVID run",
                 covid_abm_path="covid_abm",
                 run_script="user_script.py")

# Wait for it to complete
wi.run(wait_on_done=True, platform=platform)
