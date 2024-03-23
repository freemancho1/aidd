from flask import Flask
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from aidd.serving.route import Predict

app = Flask(__name__)

def main(s_port=None):
    app.debug = True
    app.add_url_rule('/predict', view_func=Predict.as_view('predict'))
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(s_port)
    print('웹서비스 준비 완료')
    IOLoop.instance().start()

    