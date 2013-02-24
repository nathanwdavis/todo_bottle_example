from bottle import Bottle, request, response, get, post, put, delete, static_file, run
import redis

from uuid import uuid4
from datetime import datetime
import json

#shared 
_redis = redis.StrictRedis()

bottle_app = Bottle()

TEST_USER_NAME = "test_user"

@bottle_app.post('/api/todos')
def create_todo():
  todo_data = request.json
  todo_data['id'] = str(uuid4())
  todo_data = normalize_todo_data(todo_data)
  if not todo_data['dueDate']:
    todo_data['dueDate'] = millis_since_epoch()

  save_todo_for_user(TEST_USER_NAME, todo_data)
  return todo_data

@bottle_app.put('/api/todos/<id>')
def update_todo(id):
  todo_data = request.json
  todo_data['id'] = id
  todo_data = normalize_todo_data(todo_data)
  save_todo_for_user(TEST_USER_NAME, todo_data)
  return todo_data

@bottle_app.delete('/api/todos/<id>')
def delete_todo(id):
  if delete_todo_for_user(TEST_USER_NAME, id):
    return {'success': True}
  else:
    return {'success': False}

@bottle_app.get('/api/todos')
def get_todos():
  response.content_type = 'application/json'
  todos = get_todos_for_user(TEST_USER_NAME)
  return serialize(todos)

@bottle_app.get('/api/labels')
def get_labels():
  labels = list(get_all_labels())
  return json_response(labels)

@bottle_app.get('/<filename:path>')
def send_static(filename):
  return static_file(filename, root='static/')


#Redis persistence

def get_todos_for_user(user, leave_raw=False):
  ids = _redis.zrange('user:'+user+':todos:bydueDate', 0, -1)
  results = _redis.hmget('all_todos', *ids)
  if not leave_raw:
    results = map(deserialize, results)
  return results

def get_all_labels():
  return _redis.smembers('all_labels')

def save_todo_for_user(user, todo):
  value = serialize(todo)
  with _redis.pipeline() as pipe:
    pipe.hset('all_todos', todo['id'], value) \
    .zadd('user:'+user+':todos:bydueDate', todo['dueDate'], todo['id'])
    if len(todo['labels']) > 0:
      print todo['labels']
      pipe.sadd('all_labels', *todo['labels'])
    pipe.execute()
  return todo

def delete_todo_for_user(user, id):
    _redis.zrem('user:'+user+':todos:bydueDate', id)
    return _redis.hdel('all_todos', id)


#utility / helpers

def serialize(thing):
  return json.dumps(thing)

def deserialize(raw):
  return json.loads(raw)

def json_response(thing):
  response.content_type = 'application/json'
  return serialize(thing)

def millis_since_epoch(dt=datetime.utcnow()):
  epoch = datetime.utcfromtimestamp(0)
  delta = dt - epoch
  return delta.total_seconds() * 1000

def normalize_todo_data(todo_data):
  def is_not_None(val): return val != None and val != '' and val != u''
  todo_data['labels'] = filter(is_not_None, todo_data['labels'])
  return todo_data

if (__name__ == '__main__'):
  #start server
  bottle_app.run(
    #server='gunicorn', 
    debug=True, reloader=True
  )