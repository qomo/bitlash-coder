import os.path
import serial
import threading
import time

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class Bitlash(threading.Thread):
    def __init__(self, serport):
        threading.Thread.__init__(self)
        self.ser = serial.Serial(serport, 57600)
        self.ser.close()
        self.ser.open()
        # self.ser.flushInput()
        # self.ser.flushOutput()
        self.thread_stop = False

    def bit_decoder(self, command):
        decoded_command = " ".join(command.split())
        # print "bit_decoder:", decoded_command, "\n"
        return decoded_command

    def to_bitlash(self, decoded_command):
        # while(not self.ser.isOpen()):
            # pass
        # self.ser.writelines("\n")
        self.ser.writelines(decoded_command+"\n")
        print "to_bitlash\n", decoded_command

    # def from_bitlash(self):
    #     outstr = ""
    #     # print "from_bitlash\n"
    #     while 1:
    #         firstchar = self.ser.read()
    #         # print "firstchar:", firstchar, "\n"
    #         if firstchar == ">":
    #             break
    #         outstr = outstr + firstchar + self.ser.readline() + "\n"
    #     return outstr

    def run(self):
        '''Read serial port and write to a file'''
        global SEROUT_BUF
        while not self.thread_stop:
            line = self.ser.readline()
            time.sleep(0.1)
            if line:
                SEROUT_BUF.append(line)

    def stop(self):
        self.thread_stop = True

    def __del__(self):
        self.ser.close()


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        # should add some output first time
        self.render('index.html')
    def post(self):
        global BITLASH
        command = self.get_argument("command", None)
        decommand = BITLASH.bit_decoder(command)
        BITLASH.to_bitlash(decommand)

class RenewHistory(tornado.web.RequestHandler):
    """Renew the history textbox."""
    def get(self):
        global SEROUT_BUF
        outstr = ""
        if SEROUT_BUF:
            outstr = outstr.join(SEROUT_BUF)
            SEROUT_BUF = []
        print outstr
        self.write(outstr)


SEROUT_BUF = []


try:
    BITLASH = Bitlash("/dev/ttyACM0")
    BITLASH.start()
except Exception, e:
    print 'open serial failed.'
    exit(1)

if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[(r'/', IndexHandler),
                (r'/renew', RenewHistory),],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
