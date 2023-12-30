from . import auth_blueprint

import datetime
from flask import request, redirect, url_for, make_response
from extensions import get_container


@auth_blueprint.route("/code", methods=["POST"])
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
