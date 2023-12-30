from . import groups_blueprint
from flask import request, redirect, url_for, render_template
from extensions import get_teams, get_permission_and_teams, get_container, random_id


@groups_blueprint.route("/group")
def write_group():
    cookie = request.cookies.get("workouts_permissions")
    permission, _ = get_permission_and_teams(cookie)

    if permission not in ["rw", "rwe"]:
        return redirect(url_for("index"), code=302)

    return render_template("group_writer.html", teams=get_teams())


@groups_blueprint.route("/group/<id>")
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


@groups_blueprint.route("/group", methods=["POST"])
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
