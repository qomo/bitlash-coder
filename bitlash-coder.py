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
        self.ser.flushInput()
        self.ser.flushOutput()
        self.thread_stop = False

    def bit_decoder(self, command):
        decoded_command = " ".join(command.split())
        # print "bit_decoder:", decoded_command, "\n"
        return decoded_command

    def to_bitlash(self, decoded_command):
        while(not self.ser.isOpen()):
            pass
        # print "to_bitlash\n", decoded_command
        self.ser.writelines(decoded_command+"\n")

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
        while not self.thread_stop:
            time.sleep(0.1)
            line = self.ser.readline()
            if line:
                self.file = open("SEROUT", 'a')
                self.file.write(line)
                self.file.close()
            # print line

    def stop(self):
        self.thread_stop = True
        # self.__del__()

    def __del__(self):
        self.ser.close()


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        # should add some output first time
        file = open("SEROUT", 'w')
        file.close()
        self.render('index.html')
    def post(self):
        global BITLASH
        # print "hello"
        # output = BITLASH.from_bitlash()
        # print output
        command = self.get_argument("command", None)
        # print "CMD:", command
        decommand = BITLASH.bit_decoder(command)
        # if "quit" in decommand:
            # BITLASH.stop()
            # exit(0)
        # print "DC:", decommand
        BITLASH.to_bitlash(decommand)
        # output = BITLASH.from_bitlash()
        # print "OUT:", output
        # self.write(output)

class RenewHistory(tornado.web.RequestHandler):
    """Renew the history textbox."""
    def get(self):
        # print "test RenewHistory"
        file = open("SEROUT", 'r')
        outstrlist = file.readlines()
        outstr = ""
        outstr = outstr.join(outstrlist)
        # print outstr
        file.close()
        self.write(outstr)


try:
    BITLASH = Bitlash("/dev/ttyUSB0")
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
