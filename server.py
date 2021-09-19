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

from http_req_parser import *
from resource_locator import ResourceLocator
from datetime import datetime
from os.path import join

class MyWebServer(socketserver.BaseRequestHandler):

    basepath = "www"
    baseurl = "http://127.0.0.1:8080"
    default_http_ver = "HTTP/1.1"

    def setup(self):
        self.httpvername = HttpReqParser.httpvername
        self.pathname = HttpReqParser.pathname
        self.hostname = HttpReqParser.hostname
        self.agentname = HttpReqParser.agentname
        self.acceptname = HttpReqParser.acceptname
    
    def handle(self):
        self.data = self.request.recv(4096).strip()
        # print ("Got a request of: %s\n" % self.data)
        # self.request.sendall(bytearray("OK",'utf-8'))

        code = -1
        http_version = self.default_http_ver
        payload = ""
        content_type = None
        extra_fields = []
        
        try:
            parsed_data = HttpReqParser.parse(self.data)
            http_version = parsed_data[self.httpvername]
            path = parsed_data[self.pathname]
            host = parsed_data[self.hostname]
            accept = parsed_data[self.acceptname]
            
        except HTTPReqParserException as e:
            code = self.mapExceptionToCode(e)

        else:
            code, payload, content_type = ResourceLocator.find(path, self.basepath)

        # if code is 301, payload contains corrected path
        if code == 301:
            corrected_path = self.baseurl + payload
            payload = ""
            location = self.create_field("Location", corrected_path)
            extra_fields.append(location)

        # check for accepted content-type
        if content_type is not None:
            content_type = "text/" + content_type

            if accept is None:
                accept = "*/*"
            
            elif content_type not in accept and "*/*" not in accept:
                code = 406
                payload = ""

        if code != 200:
            # An error occurred, Not 200 OK, Empty payload
            res = self.template_res(False, extra_fields)
            res = res.format(
                http_ver=http_version,
                status=self.get_status_str(code),
                payload=payload
            )

        else:
            # 200 OK, payload is Not empty
            res = self.template_res(more=extra_fields)
            res = res.format(
                http_ver=http_version,
                status=self.get_status_str(code),
                content_type=content_type,
                content_length=len(payload),
                payload=payload
            )

        # print("="*30)
        # print(self.data)
        # print("_"*40)
        # print(res)
        # print("="*30)

        self.request.sendall(bytearray(res, "utf-8"))

    def mapExceptionToCode(self, error):
        if type(error) is MethodNotAllowed:
            return 405

        if type(error) is UnsupportedHTTPVer:
            return 505

        if type(error) is UnsupportedPath:
            return 404

        if type(error) is BadRequest:
            return 400

    def get_status_str(self, status_code):
        if status_code == 200:
            return "200 OK"
        
        if status_code == 406:
            return "406 Not Acceptable"

        if status_code == 301:
            return "301 Moved Permanently"

        if status_code == 404:
            return "404 Not Found"

        if status_code == 405:
            return "405 Method Not Allowed"

        if status_code == 400:
            return "400 Bad Request"

        if status_code == 505:
            return "505 HTTP Version Not Supported"

    def create_field(self, field_name, field_value):
        return field_name + ": " + field_value + "\r\n"
    
    def template_res(self, has_content_type=True, more=[]):
        res = "{http_ver} {status}\r\n"
        res += "Server: localhost\r\n"

        now = datetime.now()
        formatted_now = now.strftime("%a, %d %b %Y %H:%M:%S")
        res += f"Date: {formatted_now}\r\n"
        
        if has_content_type:
            res += "Content-Type: {content_type}\r\n"
            res += "Content-Length: {content_length}\r\n"
        
        for field in more:
            res += field
        
        res += "\r\n"

        res += "{payload}"
        return res


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
