import os

from flask_autoindex import AutoIndex, Flask
from idmtools_platform_local.config import DATA_PATH
from flask_restful import Api

from idmtools_platform_local.workers.ui.controllers.experiments import Experiments
from idmtools_platform_local.workers.ui.controllers.simulations import Simulations
from idmtools_platform_local.workers.ui.utils import DateTimeEncoder

static_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static')
application = Flask(__name__, static_url_path="")
application.json_encoder = DateTimeEncoder
api = Api(application, prefix='/api')

# We setup a simple data folder browser
# We meed to manually add our rules because we don't want them at
# / and /<path>:<path>
ai = AutoIndex(application, browse_root=DATA_PATH, add_url_rules=False)


# Define where we want to render the data routes and pass those calls to AutoIndex
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
