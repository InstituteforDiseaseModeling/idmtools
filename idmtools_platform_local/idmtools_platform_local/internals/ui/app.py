"""idmtools local platform API Server.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from idmtools_platform_local.internals.ui.config import application, api, ai
from idmtools_platform_local.internals.ui.controllers.experiments import Experiments
from idmtools_platform_local.internals.ui.controllers.healthcheck import HealthCheck
from idmtools_platform_local.internals.ui.controllers.simulations import Simulations

# We setup a simple data folder browser
# We meed to manually add our rules because we don't want them at
# / and /<path>:<path>


@application.route('/data/')
@application.route('/data/<path:path>')
def autoindex(path='.'):
    """Create an autoindex from our data directory."""
    return ai.render_autoindex(path, sort_by='name', order=1)


api.add_resource(Experiments, '/experiments', '/experiments/<id>')
api.add_resource(Simulations, '/simulations', '/simulations/<id>')
api.add_resource(HealthCheck, '/healthcheck')

application.url_map.strict_slashes = False
if __name__ == "__main__":
    application.run()
