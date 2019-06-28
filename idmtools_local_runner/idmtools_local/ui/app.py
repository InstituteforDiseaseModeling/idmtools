from flask_autoindex import AutoIndex, Flask
from idmtools_local.config import DATA_PATH

application = Flask(__name__)
AutoIndex(application, browse_root=DATA_PATH)
if __name__ == "__main__":
    application.run()