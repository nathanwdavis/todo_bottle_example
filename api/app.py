from bottle import request, response, get, post, static_file, run


@get('/api/todos')
def get_todos():
  response.content_type = 'application/json'
  return '''[{
      "title": "A test todo title.",
      "dueDate": "02/19/2013",
      "labels": "one, two",
      "completed": false,
      "id": 90
    }]'''

@post('/api/todos')
def create_todo():
  
  todo_data = request.json
  #todo: save this somewhere
  todo_data['id'] = 100

  return todo_data

@get('/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static/')


run(
  #server='gunicorn', 
  host='localhost', port=8000, debug=True, reloader=True
)