from flask import Flask, make_response
from gevent.pywsgi import WSGIServer

app = Flask(__name__)

@app.route('/api/v1/hello-world-10')
def helloWord():
	return make_response("<H1>Hello Word 10</H1>", 200)


print('http://127.0.0.1:5000/api/v1/hello-world-10')
server = WSGIServer(('127.0.0.1', 5000), app)
server.serve_forever()