from . import workouts_blueprint
from flask import request, redirect, url_for, render_template, send_file, current_app
from extensions import get_container, get_permission_and_teams, random_id
import os, datetime


@workouts_blueprint.route("/list/<group_id>")
@workouts_blueprint.route("/list/<group_id>/<int:page>")
def workouts(group_id, page=1):
    groups = get_container("groups").query_items(
        query=f"SELECT * FROM groups g WHERE g.id = '{group_id}'",
        enable_cross_partition_query=True,
    )

    real_group = {}
    for group in groups:
        real_group = group

    teams = get_container("teams").query_items(
        query=f"SELECT * FROM teams t WHERE t.id = '{real_group['team_id']}'",
        enable_cross_partition_query=True,
    )

    real_team = {}
    for team in teams:
        real_team = team

    cookie = request.cookies.get("workouts_permissions")
    permission, team_ids = get_permission_and_teams(cookie)

    if real_team["id"] not in team_ids:
        return redirect(url_for("index"), code=301)

    workouts_data = list(
        get_container("workouts").query_items(
            query=f"SELECT w.id, w.date, w.title, w.distance, w.time_of_day FROM workouts w WHERE w.group_id = '{group_id}' ORDER BY w.date DESC OFFSET {(page - 1) * 10} LIMIT 10",
            enable_cross_partition_query=True,
        )
    )

    return render_template(
        "workouts_view.html",
        group_name=real_group["name"],
        team_name=real_team["name"],
        group_id=real_group["id"],
        page=page,
        workouts=workouts_data,
        should_write=permission == "rwe" or permission == "rw",
    )


@workouts_blueprint.route("/write/<group_id>", methods=["POST"])
def workout(group_id):
    id = request.form.get("id")
    if not id:
        id = random_id()
    get_container("workouts").upsert_item(
        {
            "id": id,
            "group_id": group_id,
            "title": request.form.get("title"),
            "rest_interval": request.form.get("rest_interval"),
            "date": request.form.get("date"),
            "distance": request.form.get("total_yards"),
            "time_of_day": request.form.get("timeOfDay"),
            "workout_text": request.form.get("workout_text"),
        }
    )
    return redirect(url_for("write_workout_id", id=id), code=301)


@workouts_blueprint.route("/delete/<workout_id>")
def delete_workout(workout_id):
    get_container("workouts").delete_item(item=workout_id, partition_key=workout_id)
    return redirect(url_for("index"), code=301)


@workouts_blueprint.route("/write/<group_id>")
def write_workout(group_id):
    groups = get_container("groups").query_items(
        query=f"SELECT * FROM groups g WHERE g.id = '{group_id}'",
        enable_cross_partition_query=True,
    )

    real_group = {}
    for group in groups:
        real_group = group

    if not real_group:
        return render_template("workout_writer.html")

    teams = get_container("teams").query_items(
        query=f"SELECT * FROM teams t WHERE t.id = '{real_group['team_id']}'",
        enable_cross_partition_query=True,
    )

    real_team = {}
    for team in teams:
        real_team = team

    cookie = request.cookies.get("workouts_permissions")
    permission, team_ids = get_permission_and_teams(cookie)

    if real_team["id"] not in team_ids:
        return redirect(url_for("index"), code=301)

    return render_template(
        "workout_writer.html",
        group=real_group,
        team=real_team,
        today=datetime.date.today().strftime("%Y-%m-%d"),
        should_save=permission == "rwe" or permission == "rw",
    )


@workouts_blueprint.route("/write/id/<id>")
def write_workout_id(id):
    workouts = get_container("workouts").query_items(
        query=f"SELECT * FROM workouts w WHERE w.id = '{id}'",
        enable_cross_partition_query=True,
    )

    real_workout = {}
    for workout in workouts:
        real_workout = workout

    groups = get_container("groups").query_items(
        query=f"SELECT * FROM groups g WHERE g.id = '{real_workout['group_id']}'",
        enable_cross_partition_query=True,
    )

    real_group = {}
    for group in groups:
        real_group = group

    teams = get_container("teams").query_items(
        query=f"SELECT * FROM teams t WHERE t.id = '{real_group['team_id']}'",
        enable_cross_partition_query=True,
    )

    real_team = {}
    for team in teams:
        real_team = team

    cookie = request.cookies.get("workouts_permissions")
    permission, team_ids = get_permission_and_teams(cookie)

    if real_team["id"] not in team_ids:
        return redirect(url_for("index"), code=301)

    return render_template(
        "workout_writer.html",
        id=real_workout["id"],
        team=real_team,
        group=real_group,
        date=real_workout["date"],
        today=datetime.date.today().strftime("%Y-%m-%d"),
        title=real_workout["title"],
        rest_interval=real_workout["rest_interval"],
        workout_text=real_workout["workout_text"],
        time_of_day=real_workout["time_of_day"]
        if "time_of_day" in real_workout
        else "pm",
        should_save=permission == "rwe" or permission == "rw",
    )


@workouts_blueprint.route("/seconds/download", methods=["POST"])
def download_seconds():
    seconds_json = request.form.get("seconds_json")
    id = request.form.get("id")
    file_path = os.path.join(current_app.root_path, "temp.seconds")
    with open(file_path, "w") as f:
        f.write(seconds_json)

    team = request.form.get("team")
    group = request.form.get("group")
    date = request.form.get("date")
    file_name = f"{date}-{team.lower().replace(' ', '-')}-{group.lower().replace(' ', '-')}.seconds"
    return send_file(file_path, download_name=file_name)
