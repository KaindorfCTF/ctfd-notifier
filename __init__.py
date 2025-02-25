import json
import os

from .blueprint import load_bp
from .db_utils import DBUtils
from .hooks import load_hooks
from .models import NotifierConfig

PLUGIN_PATH = os.path.dirname(__file__)
CONFIG = json.load(open(f"{PLUGIN_PATH}/config.json"))


def load(app):
    app.db.create_all()  # Create all DB entities
    DBUtils.load_default()
    bp = load_bp(CONFIG["route"])  # Load blueprint
    app.register_blueprint(bp)  # Register blueprint to the Flask app
    load_hooks()
