from . import teams_blueprint
from flask import request, render_template, redirect, url_for
from extensions import get_container, get_permission_and_teams, random_id


@teams_blueprint.route("/write")
def write_team():
    cookie = request.cookies.get("workouts_permissions")
    permission, _ = get_permission_and_teams(cookie)

    if permission != "rwe":
        return redirect(url_for("index"), code=302)

    return render_template("team_writer.html")


@teams_blueprint.route("/write/<id>")
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


@teams_blueprint.route("/create", methods=["POST"])
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
