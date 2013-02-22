from bottle import Bottle, request, response, get, post, put, delete, static_file, run
import redis

from uuid import uuid4
from datetime import datetime
import json

#shared 
_redis = redis.StrictRedis()

bottle_app = Bottle()

TEST_USER_NAME = "test_user"

@bottle_app.get('/api/todos')
def get_todos():
  response.content_type = 'application/json'
  todos = get_todos_for_user(TEST_USER_NAME)
  return serialize(todos)

@bottle_app.post('/api/todos')
def create_todo():
  todo_data = request.json
  todo_data['id'] = str(uuid4())
  if not todo_data['dueDate']:
    todo_data['dueDate'] = millis_since_epoch()

  save_todo_for_user(TEST_USER_NAME, todo_data)
  return todo_data

@bottle_app.put('/api/todos/<id>')
def update_todo(id):
  todo_data = request.json
  todo_data['id'] = id
  save_todo_for_user(TEST_USER_NAME, todo_data)
  return todo_data

@bottle_app.get('/<filename:path>')
def send_static(filename):
  return static_file(filename, root='static/')


#Redis persistence

def save_todo_for_user(user, todo):
  value = serialize(todo)
  with _redis.pipeline() as pipe:
    pipe.hset('all_todos', todo['id'], value) \
    .zadd('user:'+user+':todos:bydueDate', todo['dueDate'], todo['id']) \
    .execute()
  return todo

def get_todos_for_user(user, leave_raw=False):
  ids = _redis.zrange('user:'+user+':todos:bydueDate', 0, -1)
  results = _redis.hmget('all_todos', *ids)
  if not leave_raw:
    results = map(deserialize, results)
  return results



#utility / helpers

def serialize(thing):
  return json.dumps(thing)

def deserialize(raw):
  return json.loads(raw)

def millis_since_epoch(dt=datetime.utcnow()):
  epoch = datetime.utcfromtimestamp(0)
  delta = dt - epoch
  return delta.total_seconds() * 1000


if (__name__ == '__main__'):
  #start server
  bottle_app.run(
    #server='gunicorn', 
    debug=True, reloader=True
  )