from bottle import request, response, get, post, static_file, run
import redis

from uuid import uuid4
from datetime import datetime
import json

#shared 
_redis = redis.StrictRedis()


@get('/api/todos')
def get_todos():
  response.content_type = 'application/json'
  todos = get_todos_for_user('test_user')
  return serialize(todos)

@post('/api/todos')
def create_todo():
  todo_data = request.json
  todo_data['id'] = str(uuid4())
  print todo_data['dueDate']
  if not todo_data['dueDate']:
    print 'here'
    todo_data['dueDate'] = millis_since_epoch()

  save_todo_for_user('test_user', todo_data)

  return todo_data

@get('/<filename:path>')
def send_static(filename):
  return static_file(filename, root='static/')


#Redis persistence

def save_todo_for_user(user, todo):
  value = serialize(todo)
  return _redis.zadd(user+':todos', todo['dueDate'], value)

def get_todos_for_user(user, leave_raw=False):
  results = _redis.zrange(user+':todos', 0, -1)
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
  run(
    #server='gunicorn', 
    debug=True, reloader=True
  )