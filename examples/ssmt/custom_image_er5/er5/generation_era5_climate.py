# Example shows how SSMTWorkItem for generating ER5 climate data

import os
import sys

from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem

from idmtools_test.utils.cli import run_command


if __name__ == "__main__":
    input_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inputs")
    path_to_points_file = os.path.join(input_file_path, "climate")
    points_file = 'site_details.csv'

    # Start/end dates in one of the formats: year (2015) or year and day-of-year (2015032) or year-month-day (20150201)
    start_date = 2010
    end_date = 2012

    # Optional arguments
    optional_args = '--id-ref default --node-col id --create-asset'

    # Prepare the work item (NOT to be modified).
    docker_image = "weather-files:1.1"  # Specify the weather-tool docker image instead to use
    command_pattern = "python /app/generate_weather_asset_collection.py {} {} {} {}"
    command = command_pattern.format(points_file, start_date, end_date, optional_args)
    platform = Platform('Bayesian')
    wi = SSMTWorkItem(item_name=os.path.split(sys.argv[0])[1], docker_image=docker_image, command=command,
                      tags={'Command': command}
                      )
    # upload site_details.csv to workitem's root dir in COMPS
    wi.transient_assets.add_asset(os.path.join("climate", "site_details.csv"))
    wi.related_asset_collections
    wi.run(wait_until_done=True)

    wi_id = wi.id
    print(wi_id)
    # download generated er5 climate files to local "output_er5" folder by download cli util
    result = run_command('comps', 'Bayesian', 'download', '--work-item', wi_id,
                         '--name', 'download_er5_climate', '--output-path', 'output_er5', '--pattern', '**/*.json', '--pattern',
                         '**/*.bin')

