import os
from flask import g
from azure.cosmos import CosmosClient


def random_id(N=20):
    import string
    import random

    return "".join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits)
        for _ in range(N)
    )


def can_be_float(num):
    try:
        fl_num = float(num)
        return True if fl_num > 0.0 else False
    except ValueError:
        return False


def get_client():
    if not hasattr(g, "client"):
        URL = os.environ["COSMOS_URI"]
        KEY = os.environ["COSMOS_KEY"]
        g.client = CosmosClient(URL, credential=KEY)
    return g.client


def get_db():
    if not hasattr(g, "database"):
        g.database = get_client().get_database_client("db")
    return g.database


def get_container(name):
    container_global_name = f"container_{name}"
    if not hasattr(g, container_global_name):
        setattr(g, container_global_name, get_db().get_container_client(name))
    return getattr(g, container_global_name)


def get_groups():
    return list(
        get_container("groups").query_items(
            query="SELECT * FROM groups g", enable_cross_partition_query=True
        )
    )


def get_teams():
    return list(
        get_container("teams").query_items(
            query="SELECT * FROM teams t", enable_cross_partition_query=True
        )
    )


def get_permission_and_teams(cookie):
    permission = None
    team_ids = None
    if cookie:
        permissions = list(
            get_container("code_to_permission").query_items(
                query=f"SELECT * FROM code_to_permission c WHERE c.cookie = '{cookie}'",
                enable_cross_partition_query=True,
            )
        )
        if len(permissions) > 0:
            permission = permissions[0]["permission"]
            team_ids = permissions[0]["team_ids"]
    return permission, team_ids
