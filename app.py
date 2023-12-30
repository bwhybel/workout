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
import datetime
import os

from extensions import get_container, get_permission_and_teams, get_teams, random_id

app = Flask(__name__)
app.register_blueprint(workouts_blueprint, url_prefix="/workouts")


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


@app.route("/team")
def write_team():
    cookie = request.cookies.get("workouts_permissions")
    permission, _ = get_permission_and_teams(cookie)

    if permission != "rwe":
        return redirect(url_for("index"), code=302)

    return render_template("team_writer.html")


@app.route("/team/<id>")
def write_team_id(id):
    cookie = request.cookies.get("workouts_permissions")
    permission, _ = get_permission_and_teams(cookie)

    if permission != "rwe":
        return redirect(url_for("index"), code=302)

    teams = get_container("teams").query_items(
        query=f"SELECT * FROM teams t WHERE t.id = '{id}'",
        enable_cross_partition_query=True,
    )

    real_team = {}
    for team in teams:
        real_team = team

    return render_template(
        "team_writer.html",
        id=real_team["id"],
        name=real_team["name"],
        code=real_team["code"],
        image=real_team["image"],
        logo_width=real_team["logo_width"],
    )


@app.route("/team", methods=["POST"])
def team():
    id = request.form.get("id")
    if not id:
        id = random_id()
    name = request.form.get("name")
    code = request.form.get("code")
    image = request.form.get("image")
    logo_width = request.form.get("logo_width")
    get_container("teams").upsert_item(
        {"id": id, "name": name, "code": code, "image": image, "logo_width": logo_width}
    )
    return redirect(url_for("write_team_id", id=id), code=301)


@app.route("/code", methods=["POST"])
def code():
    expiration_date = datetime.datetime.now() + datetime.timedelta(days=30)
    code = request.form.get("code")

    codes = list(
        get_container("code_to_permission").query_items(
            query=f"SELECT * FROM code_to_permission c WHERE c.id = '{code}'",
            enable_cross_partition_query=True,
        )
    )

    if len(codes) == 0:
        return redirect(url_for("index"), code=301)

    cookie_value = codes[0]["cookie"]

    response = make_response(redirect(url_for("index"), code=301))
    response.set_cookie(
        "workouts_permissions", value=cookie_value, expires=expiration_date
    )
    return response


@app.route("/group")
def write_group():
    cookie = request.cookies.get("workouts_permissions")
    permission, _ = get_permission_and_teams(cookie)

    if permission not in ["rw", "rwe"]:
        return redirect(url_for("index"), code=302)

    return render_template("group_writer.html", teams=get_teams())


@app.route("/group/<id>")
def write_group_id(id):
    cookie = request.cookies.get("workouts_permissions")
    permission, _ = get_permission_and_teams(cookie)

    if permission not in ["rw", "rwe"]:
        return redirect(url_for("index"), code=302)

    groups = get_container("groups").query_items(
        query=f"SELECT * FROM groups g WHERE g.id = '{id}'",
        enable_cross_partition_query=True,
    )

    real_group = {}
    for group in groups:
        real_group = group

    return render_template(
        "group_writer.html",
        id=real_group["id"],
        name=real_group["name"],
        code=real_group["code"],
        teams=get_teams(),
        team_id=real_group["team_id"],
    )


@app.route("/group", methods=["POST"])
def group():
    id = request.form.get("id")
    if not id:
        id = random_id()
    name = request.form.get("name")
    code = request.form.get("code")
    team = request.form.get("team")

    cookie = request.cookies.get("workouts_permissions")
    permission, team_ids = get_permission_and_teams(cookie)
    if (permission != "rw" and permission != "rwe") or team not in team_ids:
        return redirect(url_for("index"), code=301)

    get_container("groups").upsert_item(
        {"id": id, "name": name, "code": code, "team_id": team}
    )
    return redirect(url_for("write_group_id", id=id), code=301)


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


if __name__ == "__main__":
    app.run()
