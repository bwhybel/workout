from flask import Blueprint

teams_blueprint = Blueprint("teams", __name__, template_folder="templates")

from . import views
