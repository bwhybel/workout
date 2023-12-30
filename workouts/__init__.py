from flask import Blueprint

workouts_blueprint = Blueprint(
    "workouts", __name__, template_folder="templates", static_folder="static"
)

from . import views
