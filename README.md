todo_bottle_example
===================

Yet another ToDo example app - this one built with: 

 - Bottle ( http://bottlepy.org )
 - Bootstrap
 - Backbone
 - Persistence in Redis

To get this up and running for yourself:

 - 'pip install -r pip_requirements.txt' to get the dependencies installed
 - start up a Redis server ('redis-server')
 - 'python api/app.py' to start the built-in web server

To run the tests:

 - start a Redis server on the non-default port 6389: 'redis-server -p 6389'
 - from the root of the repo: 'nosetests'