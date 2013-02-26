from bottle import Bottle, request, response, get, post, put, delete, redirect, static_file, run
import redis
from base64 import b64encode, b64decode
from Crypto.Cipher import AES

from uuid import uuid4
from datetime import datetime
import json

#shared 
_redis = redis.StrictRedis()

bottle_app = Bottle()

TEST_USER_NAME = "test_user"
SECRET_KEY = "your very secret key goes here.."

@bottle_app.post('/api/todos')
def create_todo():
  if not authorized():
    return unauthorized_response()
  todo_data = request.json
  todo_data['id'] = str(uuid4())
  todo_data = normalize_todo_data(todo_data)
  if not todo_data['dueDate']:
    todo_data['dueDate'] = millis_since_epoch()

  save_todo_for_user(TEST_USER_NAME, todo_data)
  return todo_data

@bottle_app.put('/api/todos/<id>')
def update_todo(id):
  if not authorized():
    return unauthorized_response()
  todo_data = request.json
  todo_data['id'] = id
  todo_data = normalize_todo_data(todo_data)
  save_todo_for_user(TEST_USER_NAME, todo_data)
  return todo_data

@bottle_app.delete('/api/todos/<id>')
def delete_todo(id):
  if not authorized():
    return unauthorized_response()
  if delete_todo_for_user(TEST_USER_NAME, id):
    return {'success': True}
  else:
    return {'success': False}

@bottle_app.get('/api/todos')
def get_todos():
  if not authorized():
    return unauthorized_response()
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

#Auth

@bottle_app.post('/api/login')
def handle_login():
  username = request.POST.get('username', '').strip()
  password = request.POST.get('password', '').strip()
  redirect_to = request.POST.get('redirectto', '').strip()
  #todo: validate u/p pair
  auth_token = build_auth_token(username)
  response.set_cookie('auth_token', auth_token)
  if len(redirect_to) > 0:
    redirect("/index.html")
  else: return {'auth_token': auth_token}
  
def authorized():
  token = request.cookies.get('auth_token')
  if not token: token = request.params.get('auth_token')

  if token:
    username = extract_username_from_token(token)
    request.environ['this_app.current_user'] = username
    return True
  else:
    response.status = '403 Unauthorized request'
    return False

def unauthorized_response():
  return {'error_message': 'Unauthorized request. Please login.'}

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

def build_cipher():
  cipher = AES.new(SECRET_KEY, AES.MODE_CFB, 'ur_secrt' * (AES.block_size / 8))
  return cipher

def encrypt(data):
  cipher = build_cipher()
  c = cipher.encrypt(data)
  e = b64encode(c)
  del cipher
  return e

def decrypt(data):
  cipher = build_cipher()
  d = b64decode(data)
  p = cipher.decrypt(d)
  del cipher
  return p

def build_auth_token(username):
  return encrypt(username+":|:"+str(millis_since_epoch()))

def extract_username_from_token(auth_token):
  decrypted = decrypt(auth_token)
  pieces = decrypted.split(':|:')
  return pieces[0]

if (__name__ == '__main__'):
  #start server
  bottle_app.run(
    #server='gunicorn', 
    debug=True, reloader=True
  )