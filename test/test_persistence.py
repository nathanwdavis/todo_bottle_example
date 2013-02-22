from nose import with_setup
from api import app
import redis

def setup():
  app._redis = redis.StrictRedis(port=6389)
  app._redis.flushdb()
  print app.redis

def test_save_todo_for_user():
  user = "test_user"
  todo = {      
    'id': 'abc123efg456hij789__',
    'title': 'A test thing to do.',
    'dueDate': 1362355210001,
    'labels': [
      'test_label1', 
      'test_label2'
    ],
    'completed': False
  }
  result = app.save_todo_for_user(user, todo)
  print(result)
  assert(result)


def setup_test_get_todos_for_user():
  app._redis.flushdb()
  user = "test_user"
  todo1 = {      
    'id': 'abc123efg456hij789__',
    'title': 'A test thing to do.',
    'dueDate': 1362355210011,
    'labels': [
      'test_label1', 
      'test_label2'
    ],
    'completed': False
  }
  app.save_todo_for_user(user, todo1)
  todo2 = {      
    'id': 'bbc123efg456hij789__',
    'title': 'A test thing to do #2.',
    'dueDate': 1362355210001,
    'labels': [
      'test_label3', 
      'test_label2'
    ],
    'completed': False
  }
  app.save_todo_for_user(user, todo2)

@with_setup(setup_test_get_todos_for_user)
def test_get_todos_for_user():
  user = "test_user"
  result = app.get_todos_for_user(user)
  assert len(result) == 2
  #default sort should put bbc123efg456hij789__ first
  assert result[0]['id'] == 'bbc123efg456hij789__'

@with_setup(setup_test_get_todos_for_user)
def test_get_todos_for_user_with_leave_raw_true():
  user = "test_user"
  result = app.get_todos_for_user(user, leave_raw=True)
  assert len(result) == 2
  assert type(result[0]) == type("")
