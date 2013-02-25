from api import app
from datetime import datetime

_test_todo = {      
  'id': 'cbc123efg456hij789__',
  'title': 'A test to do for serialization testing',
  'dueDate': 1362355210001,
  'labels': [
    'test_label2', 
    'test_label3'
  ],
  'completed': False
}

def test_todo_serialization():
  raw = app.serialize(_test_todo)
  resurrected = app.deserialize(raw)
  assert resurrected == _test_todo

def test_millis_since_epoch_with_default_args():
  assert app.millis_since_epoch()

def test_millis_since_epoch_with_specific_datetime():
  expected_millis = 1357017330000.0
  dt = datetime(2013,1,1,5,15,30)
  actual_millis = app.millis_since_epoch(dt)
  assert actual_millis == expected_millis

def test_normalize_todo_data():
  test_todo = _test_todo
  test_todo['labels'].append('')
  assert len(test_todo['labels']) == 3
  print test_todo
  test_todo = app.normalize_todo_data(test_todo)
  assert len(test_todo['labels']) == 2

def test_encrypt_decrypt():
  data = 'abc123def456'
  encrypted = app.encrypt(data)
  assert encrypted
  decrypted = app.decrypt(encrypted)
  assert decrypted == data