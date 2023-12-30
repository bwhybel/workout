from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory,
    make_response,
)

from workouts import workouts_blueprint
from teams import teams_blueprint
from groups import groups_blueprint
from auth import auth_blueprint
import datetime
import os

from extensions import get_container, get_permission_and_teams, get_teams, random_id

app = Flask(__name__)
app.register_blueprint(workouts_blueprint, url_prefix="/workouts")
app.register_blueprint(teams_blueprint, url_prefix="/teams")
app.register_blueprint(groups_blueprint, url_prefix="/groups")
app.register_blueprint(auth_blueprint, url_prefix="/auth")


@app.route("/")
def index():
    cookie = request.cookies.get("workouts_permissions")
    permission, team_ids = get_permission_and_teams(cookie)

    team_ids_to_groups = {}
    team_ids_to_names = {}
    if team_ids:
        for team_id in team_ids:
            team = list(
                get_container("teams").query_items(
                    query=f"SELECT * FROM teams t WHERE t.id = '{team_id}'",
                    enable_cross_partition_query=True,
                )
            )[0]

            groups = get_container("groups").query_items(
                query=f"SELECT * FROM groups g WHERE g.team_id = '{team_id}'",
                enable_cross_partition_query=True,
            )

            team_ids_to_groups[team["id"]] = list(groups)
            team_ids_to_names[team["id"]] = team["name"]

    return render_template(
        "index.html",
        team_ids_to_groups=team_ids_to_groups,
        team_ids_to_names=team_ids_to_names,
        should_edit_teams=permission == "rwe",
        should_edit_groups=permission == "rw" or permission == "rwe",
        should_write_workouts=permission == "rw" or permission == "rwe",
        should_create_new_teams=permission == "rwe",
        should_create_new_groups=permission == "rw" or permission == "rwe",
    )


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


if __name__ == "__main__":
    app.run()
