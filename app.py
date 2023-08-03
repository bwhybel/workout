from flask import Flask, render_template, request, redirect, url_for, send_from_directory, g, current_app, send_file, make_response
from azure.cosmos import CosmosClient
import datetime
import time
import json
import os

app = Flask(__name__)

def random_id(N = 20):
  import string, random
  return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

def can_be_float(num):
  try:
    fl_num = float(num)
    return True if fl_num > 0.0 else False
  except ValueError:
    return False

def get_client():
  if not hasattr(g, 'client'):
    URL = os.environ["COSMOS_URI"]
    KEY = os.environ["COSMOS_KEY"]
    g.client = CosmosClient(URL, credential = KEY)
  return g.client


def get_db():
  if not hasattr(g, 'database'):
    g.database = get_client().get_database_client('db')
  return g.database


def get_container(name):
  container_global_name = f'container_{name}'
  if not hasattr(g, container_global_name):
    setattr(g, container_global_name, get_db().get_container_client(name))
  return getattr(g, container_global_name)


def get_groups():
  return list(
    get_container('groups').query_items(
      query = 'SELECT * FROM groups g',
      enable_cross_partition_query = True
    )
  )

def get_teams():
  return list(
    get_container('teams').query_items(
      query = 'SELECT * FROM teams t',
      enable_cross_partition_query = True
    )
  )

def get_permission_and_teams(cookie):
  permission = None
  team_ids = None
  if cookie:
    permissions = list(get_container('code_to_permission').query_items(
      query = f"SELECT * FROM code_to_permission c WHERE c.cookie = '{cookie}'",
      enable_cross_partition_query = True
    ))
    if len(permissions) > 0:
      permission = permissions[0]['permission']
      team_ids = permissions[0]['team_ids']
  return permission, team_ids


@app.route('/')
def index():
  cookie = request.cookies.get('workouts_permissions')
  permission, team_ids = get_permission_and_teams(cookie)

  team_ids_to_groups = {}
  team_ids_to_names = {}
  if team_ids:
    for team_id in team_ids:
      team = list(get_container('teams').query_items(
        query = f"SELECT * FROM teams t WHERE t.id = '{team_id}'",
        enable_cross_partition_query = True
      ))[0]

      groups = get_container('groups').query_items(
        query = f"SELECT * FROM groups g WHERE g.team_id = '{team_id}'",
        enable_cross_partition_query = True
      )
      
      team_ids_to_groups[team['id']] = list(groups)
      team_ids_to_names[team['id']] = team['name']

  return render_template(
    'index.html',
    team_ids_to_groups = team_ids_to_groups,
    team_ids_to_names = team_ids_to_names,
    should_edit_teams = permission == 'rwe',
    should_edit_groups = permission == 'rw' or permission == 'rwe',
    should_write_workouts = permission == 'rw' or permission == 'rwe',
    should_create_new_teams = permission == 'rwe',
    should_create_new_groups = permission == 'rw' or permission == 'rwe'
  )


@app.route('/team')
def write_team():
  cookie = request.cookies.get('workouts_permissions')
  permission, _ = get_permission_and_teams(cookie)

  if permission != 'rwe':
    return redirect(url_for('index'), code = 302)

  return render_template('team_writer.html')


@app.route('/team/<id>')
def write_team_id(id):
  cookie = request.cookies.get('workouts_permissions')
  permission, _ = get_permission_and_teams(cookie)

  if permission != 'rwe':
    return redirect(url_for('index'), code = 302)

  teams = get_container('teams').query_items(
    query = f"SELECT * FROM teams t WHERE t.id = '{id}'",
    enable_cross_partition_query = True
  )

  real_team = {}
  for team in teams:
    real_team = team

  return render_template(
    'team_writer.html',
    id = real_team['id'],
    name = real_team['name'],
    code = real_team['code'],
    image = real_team['image'],
    logo_width = real_team['logo_width']
  )


@app.route('/team', methods = ['POST'])
def team():
  id = request.form.get('id')
  if not id:
    id = random_id()
  name = request.form.get('name')
  code = request.form.get('code')
  image = request.form.get('image')
  logo_width = request.form.get('logo_width')
  get_container('teams').upsert_item(
    {
      'id': id,
      'name': name,
      'code': code,
      'image': image,
      'logo_width': logo_width
    }
  )
  return redirect(url_for('write_team_id', id = id), code = 301)

@app.route('/code', methods = ['POST'])
def code():
  expiration_date = datetime.datetime.now() + datetime.timedelta(days = 30)
  code = request.form.get('code')

  codes = list(get_container('code_to_permission').query_items(
    query = f"SELECT * FROM code_to_permission c WHERE c.id = '{code}'",
    enable_cross_partition_query = True
  ))

  if len(codes) == 0:
    return redirect(url_for('index'), code = 301)

  cookie_value = codes[0]['cookie']

  response = make_response(redirect(url_for('index'), code = 301))
  response.set_cookie('workouts_permissions', value = cookie_value, expires = expiration_date)
  return response


@app.route('/group')
def write_group():
  cookie = request.cookies.get('workouts_permissions')
  permission, _ = get_permission_and_teams(cookie)

  if permission not in ['rw', 'rwe']:
    return redirect(url_for('index'), code = 302)

  return render_template('group_writer.html', teams = get_teams())


@app.route('/group/<id>')
def write_group_id(id):
  cookie = request.cookies.get('workouts_permissions')
  permission, _ = get_permission_and_teams(cookie)

  if permission not in ['rw', 'rwe']:
    return redirect(url_for('index'), code = 302)

  groups = get_container('groups').query_items(
    query = f"SELECT * FROM groups g WHERE g.id = '{id}'",
    enable_cross_partition_query = True
  )

  real_group = {}
  for group in groups:
    real_group = group

  return render_template(
    'group_writer.html',
    id = real_group['id'],
    name = real_group['name'],
    code = real_group['code'],
    teams = get_teams(),
    team_id = real_group['team_id']
  )


@app.route('/group', methods = ['POST'])
def group():
  id = request.form.get('id')
  if not id:
    id = random_id()
  name = request.form.get('name')
  code = request.form.get('code')
  team = request.form.get('team')

  cookie = request.cookies.get('workouts_permissions')
  permission, team_ids = get_permission_and_teams(cookie)
  if (permission != 'rw' and permission != 'rwe') or team not in team_ids:
    return redirect(url_for('index'), code = 301)

  get_container('groups').upsert_item(
    {
      'id': id,
      'name': name,
      'code': code,
      'team_id': team
    }
  )
  return redirect(url_for('write_group_id', id = id), code = 301)

@app.route('/workouts/<group_id>')
@app.route('/workouts/<group_id>/<int:page>')
def workouts(group_id, page = 1):
  groups = get_container('groups').query_items(
    query = f"SELECT * FROM groups g WHERE g.id = '{group_id}'",
    enable_cross_partition_query = True
  )

  real_group = {}
  for group in groups:
    real_group = group

  teams = get_container('teams').query_items(
    query = f"SELECT * FROM teams t WHERE t.id = '{real_group['team_id']}'",
    enable_cross_partition_query = True
  )

  real_team = {}
  for team in teams:
    real_team = team

  cookie = request.cookies.get('workouts_permissions')
  permission, team_ids = get_permission_and_teams(cookie)

  if real_team['id'] not in team_ids:
    return redirect(url_for('index'), code = 301)

  workouts_data = list(
    get_container('workouts').query_items(
      query = f"SELECT w.id, w.date, w.title, w.distance FROM workouts w WHERE w.group_id = '{group_id}' ORDER BY w.date DESC OFFSET {(page - 1) * 10} LIMIT 10",
      enable_cross_partition_query = True
    )
  )

  return render_template(
    'workouts_view.html',
    group_name = real_group['name'],
    team_name = real_team['name'],
    group_id = real_group['id'],
    page = page,
    workouts = workouts_data,
    should_write = permission == 'rwe' or permission == 'rw'
  )


@app.route('/workout/<group_id>', methods = ['POST'])
def workout(group_id):
  id = request.form.get('id')
  if not id:
    id = random_id()
  get_container('workouts').upsert_item(
    {
      'id': id,
      'group_id': group_id,
      'title': request.form.get('title'),
      'rest_interval': request.form.get('rest_interval'),
      'date': request.form.get('date'),
      'distance': request.form.get('total_yards'),
      'workout_text': request.form.get('workout_text')
    }
  )
  return redirect(url_for('write_workout_id', id = id), code = 301)

@app.route('/delete_workout/<workout_id>')
def delete_workout(workout_id):
  get_container('workouts').delete_item(item = workout_id, partition_key = workout_id)
  return redirect(url_for('index'), code = 301)


@app.route('/workout/<group_id>')
def write_workout(group_id):
  groups = get_container('groups').query_items(
    query = f"SELECT * FROM groups g WHERE g.id = '{group_id}'",
    enable_cross_partition_query = True
  )

  real_group = {}
  for group in groups:
    real_group = group

  if not real_group:
    return render_template(
      'workout_writer.html'
    )

  teams = get_container('teams').query_items(
    query = f"SELECT * FROM teams t WHERE t.id = '{real_group['team_id']}'",
    enable_cross_partition_query = True
  )

  real_team = {}
  for team in teams:
    real_team = team

  cookie = request.cookies.get('workouts_permissions')
  permission, team_ids = get_permission_and_teams(cookie)

  if real_team['id'] not in team_ids:
    return redirect(url_for('index'), code = 301)

  return render_template(
    'workout_writer.html',
    group = real_group,
    team = real_team,
    today = datetime.date.today().strftime("%Y-%m-%d"),
    should_save = permission == 'rwe' or permission == 'rw'
  )


@app.route('/workout/id/<id>')
def write_workout_id(id):
  workouts = get_container('workouts').query_items(
    query = f"SELECT * FROM workouts w WHERE w.id = '{id}'",
    enable_cross_partition_query = True
  )

  real_workout = {}
  for workout in workouts:
    real_workout = workout

  groups = get_container('groups').query_items(
    query = f"SELECT * FROM groups g WHERE g.id = '{real_workout['group_id']}'",
    enable_cross_partition_query = True
  )

  real_group = {}
  for group in groups:
    real_group = group

  teams = get_container('teams').query_items(
    query = f"SELECT * FROM teams t WHERE t.id = '{real_group['team_id']}'",
    enable_cross_partition_query = True
  )

  real_team = {}
  for team in teams:
    real_team = team

  cookie = request.cookies.get('workouts_permissions')
  permission, team_ids = get_permission_and_teams(cookie)

  if real_team['id'] not in team_ids:
    return redirect(url_for('index'), code = 301)

  return render_template(
    'workout_writer.html',
    id = real_workout['id'],
    team = real_team,
    group = real_group,
    date = real_workout['date'],
    today = datetime.date.today().strftime("%Y-%m-%d"),
    title = real_workout['title'],
    rest_interval = real_workout['rest_interval'],
    workout_text = real_workout['workout_text'],
    should_save = permission == 'rwe' or permission == 'rw'
  )

@app.route('/seconds/download', methods = ['POST'])
def download_seconds():
  seconds_json = request.form.get('seconds_json')
  id = request.form.get('id')
  file_path = os.path.join(current_app.root_path, 'temp.seconds')
  with open(file_path, 'w') as f:
    f.write(seconds_json)

  group = request.form.get('group')
  date = request.form.get('date')
  file_name = f"{date}-{group.lower().replace(' ', '-')}.seconds"
  return send_file(file_path, download_name = file_name)


@app.route('/wk3/download', methods = ['POST'])
def download_wk3():
  wk3_text = request.form.get('wk3_text')
  id = request.form.get('id')
  file_path = os.path.join(current_app.root_path, 'temp.wk3')
  with open(file_path, 'w') as f:
    f.write(wk3_text)

  group = request.form.get('group')
  date = request.form.get('date')
  file_name = f"{date}-{group.lower().replace(' ', '-')}.wk3"
  return send_file(file_path, download_name = file_name)


@app.route('/favicon.ico')
def favicon():
  return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype = 'image/vnd.microsoft.icon')


if __name__ == '__main__':
  app.run()
