#  coding: utf-8 
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

from http_req_parser import HttpReqParser
from datetime import date
from os.path import join

class MyWebServer(socketserver.BaseRequestHandler):

    basepath = "./www"
    index = join(basepath, "index.html")
    basecss = join(basepath, "base.css")
    
    def handle(self):
        self.data = self.request.recv(4096).strip()
        # print ("Got a request of: %s\n" % self.data)
        # self.request.sendall(bytearray("OK",'utf-8'))

        res = self.template_res()

        httpvername = HttpReqParser.httpvername
        pathname = HttpReqParser.pathname
        hostname = HttpReqParser.hostname
        agentname = HttpReqParser.agentname
        acceptname = HttpReqParser.accepname

        try:
            parsed_data = HttpReqParser.parse(self.data)
            http_version = parsed_data[httpvername]
            path = parsed_data[pathname]
            host = parsed_data[hostname]
            accept = parsed_data[acceptname]

            if path == "/" or path == "/index.html":
                index_f = open(self.index)
                payload = index_f.read()

                res = res.format(
                    http_ver=http_version, 
                    status=self.get_status_str(200), 
                    content_type="text/html",
                    payload=payload
                )

            if path == "/base.css":
                css_f = open(self.basecss)
                payload = css_f.readlines()

                res = res.format(
                    http_ver=http_version,
                    status=self.get_status_str(200),
                    content_type="text/css",
                    payload=payload
                )


            self.request.sendall(bytearray(res, "utf-8"))

        except Exception as e:
            print(e.args)
    
    def get_status_str(self, status_code):
        if status_code == 200:
            return "200 OK"
    
    def template_res(self):
        res = "{http_ver} {status}\r\n"
        res += "Server: localhost\r\n"
        res += f"Date: {date.today()}\r\n"
        res += "Content-Type: {content_type}\r\n\r\n"
        res += "{payload}"
        return res

    def handle_get(self):
        pass

    def handle_bad_req(self):
        pass


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
