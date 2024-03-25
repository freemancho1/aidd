from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from aidd.sys.utils import AiddInit as aidd_init
from aidd.sys.argvs import serving_argvs
import aidd.sys.messages as msg
from aidd.serving.rest_server import app

def main(s_port=None):
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(s_port)
    print(f'{msg.SYS["WEB_SERVICE_COMPLETED"]}{s_port}')
    IOLoop.instance().start()
    
if __name__ == '__main__':
    aidd_init()
    args = serving_argvs()
    main(s_port=args.port)