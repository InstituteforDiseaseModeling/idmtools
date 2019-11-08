from idmtools_platform_local.internals.ui.config import application, api, ai, db
from idmtools_platform_local.internals.ui.controllers.experiments import Experiments
from idmtools_platform_local.internals.ui.controllers.simulations import Simulations

# We setup a simple data folder browser
# We meed to manually add our rules because we don't want them at
# / and /<path>:<path>


@application.route('/data/')
@application.route('/data/<path:path>')
def autoindex(path='.'):
    return ai.render_autoindex(path, sort_by='name', order=1)


@application.route('/')
def index():
    return application.send_static_file('index.html')


api.add_resource(Experiments, '/experiments', '/experiments/<id>')
api.add_resource(Simulations, '/simulations', '/simulations/<id>')

application.url_map.strict_slashes = False
if __name__ == "__main__":
    application.run()
