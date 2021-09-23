# Copyright 2021 Olivier Vadiavaloo
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

class HTTPReqParserException(Exception):

    def __init__(self, message=""):
        self.message = message

class MethodNotAllowed(HTTPReqParserException):
    pass

class UnsupportedHTTPVer(HTTPReqParserException):
    pass

class UnsupportedPath(HTTPReqParserException):
    pass

class BadRequest(HTTPReqParserException):
    pass

class HttpReqParser:
    methodname = "HTTP_METHOD"
    pathname = "PATH"
    httpvername = "HTTP_VER"
    hostname = "HOST"
    agentname = "AGENT"
    acceptname = "ACCEPT"

    @classmethod
    def parse(cls, unparsed_data):
        parsed_data = {}

        # Check for empty byte string
        if not unparsed_data:
            raise BadRequest

        # Decode unparsed data
        decoded_u_data = unparsed_data.decode("utf-8")

        # Split over CR-LF
        splitted_data = decoded_u_data.split("\r\n\r\n")
        splitted_data = splitted_data[0].split("\r\n")
        splitted_data_len = len(splitted_data)
        
        start_line = splitted_data[0]
        
        # Check method name
        start_line = cls.check_strip(
            start_line,
            "GET",
            MethodNotAllowed,
            strip_end=" "
        )
        parsed_data[cls.methodname] = True

        # Get path
        path = cls.get_substr(
            start_line,
            " ",
            UnsupportedPath
        )

        if path[0] != "/":
            raise UnsupportedPath

        start_line = start_line.replace(path+" ", "", 1)
        parsed_data[cls.pathname] = path
        
        # Check HTTP version
        start_line, http_ver = cls.check_strip_multi(
            start_line,
            ["HTTP/1.1", "HTTP/1.0"],
            UnsupportedHTTPVer,
            strip_end=" "
        )

        if splitted_data_len == 1 and http_ver == "HTTP/1.0":
            raise BadRequest

        parsed_data[cls.httpvername] = http_ver

        fields = splitted_data[1:]

        # Get host
        host = cls.get_field(fields, "Host")
        if host is None:
            raise BadRequest

        parsed_data[cls.hostname] = host

        # Get some other fields (Accept, User-Agent)
        accept = cls.get_field(fields, "Accept")
        agent = cls.get_field(fields, "User-Agent")

        parsed_data[cls.acceptname] = accept
        parsed_data[cls.agentname] = agent

        return parsed_data

    @classmethod
    def get_field(cls, fields, field_str):
        for field in fields:
            splitted_field = field.split(": ")
            if len(splitted_field) == 1:
                raise BadRequest
            
            if field_str == splitted_field[0]:
                return splitted_field[1]

        return None           

    @classmethod
    def check_strip(cls, target_str, check_str, error,
        strip_end="", index=0):
        if target_str.find(check_str) != index:
            raise error

        return target_str.replace(check_str + strip_end, "", 1)

    @classmethod
    def check_strip_multi(cls, target_str, check_strs, error,
        strip_end="", index=0):
        target_str_len = len(target_str)
        count = 0
        for check_str in check_strs:
            try:
                stripped_target_str = cls.check_strip(
                    target_str,
                    check_str,
                    error,
                    strip_end,
                    index
                )

                return stripped_target_str, check_str

            except HTTPReqParserException:
                if count == target_str_len:
                    raise error

    @classmethod
    def get_substr(cls, target_str, end, error):
        substr = ""
        char = ""
        for char in target_str:
            if char == end:
                return substr
            
            substr += char

        raise error

# DEBUG CODE:
# Uncomment and run http_req_parser.py
# request can be changed to contain the desired headers
# Prints out the result of the parsing
# if __name__ == "__main__":
#     request = b"GET / HTTP/1.1\r\nHost: slashdot.org\r\nAccept: python\r\nAgent: text/html\r\n\r\n"
#     parsed_data = HttpReqParser.parse(request)
    
#     for items in parsed_data.items():
#         print(items)