from api import app
from webtest import TestApp, AppError
import json

wsgi = TestApp(app.bottle_app)

def test_wsgi_get_todos_success():
  resp = wsgi.get('/api/todos')
  assert resp.status_code == 200

def test_wsgi_post_todo_success():
  post_data = dict(
    title='a test todo title',
    dueDate=1362355210010,
    labels=[
      'test_label1', 
      'test_label2'
    ],
    completed=False
  )
  resp = wsgi.post_json('/api/todos', post_data)
  assert resp.status_code == 200

def test_wsgi_put_todo_success():
  dueDate = 1362355210010
  post_data = dict(
    title='a test todo title',
    dueDate=dueDate,
    labels=[
      'test_label1', 
      'test_label2'
    ],
    completed=False
  )
  resp = wsgi.post_json('/api/todos', post_data)
  new_id = str(resp.json['id'])
  post_data['id'] = new_id
  post_data['dueDate'] = dueDate + 10
  resp = wsgi.put_json('/api/todos/'+new_id, post_data)
  assert resp.status_code == 200
  assert int(resp.json['dueDate']) == dueDate + 10
