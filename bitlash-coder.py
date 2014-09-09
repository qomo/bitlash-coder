import os.path
import serial

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class Bitlash:
    def __init__(self, serport):
        self.ser = serial.Serial(serport, 57600)

    def bit_decoder(self, command):
        decoded_command = " ".join(command.split())
        return decoded_command

    def to_bitlash(self, decoded_command):
        while(not self.ser.isOpen()):
            pass
        self.ser.writelines(decoded_command+"\n")

    def from_bitlash(self):
        outstr = ""
        self.ser.readline()
        # print 1
        while 1:
            firstchar = self.ser.read()
            # print "while"
            if firstchar == ">":
                break
            outstr = outstr + firstchar + self.ser.readline() + "\n"
        return outstr

    def __del__(self):
        self.ser.close()


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')
    def post(self):
        bitlash = Bitlash("/dev/ttyUSB0")
        command = self.get_argument("command", None)
        decommand = bitlash.bit_decoder(command)
        bitlash.to_bitlash(decommand)
        output = bitlash.from_bitlash()
        bitlash.__del__()
        # self.write(" ".join(command.split()))
        self.write(output)


if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[(r'/', IndexHandler), ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
