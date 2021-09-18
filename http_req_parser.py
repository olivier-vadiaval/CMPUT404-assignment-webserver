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

class HttpReqParser:
    methodname = "HTTP_METHOD"
    pathname = "PATH"
    httpvername = "HTTP_VER"
    hostname = "HOST"
    agentname = "AGENT"
    accepname = "ACCEPT"
    fields = ["Host", "User-Agent", "Accept"]

    METHOD_ERR = "Wrong method"
    PATH_ERR = "Wrong path"
    HTTPVER_ERR = "Wrong http version"
    FIELD_ERR = "Required field not specified"
    PARSE_ERR = "Parsing error"

    @classmethod
    def parse(cls, unparsed_data):
        parsed_data = {}

        # decode unparsed data
        decoded_u_data = unparsed_data.decode("utf-8")
        decoded_u_data += "\r\n\r\n"

        try:
            # check method is GET
            decoded_u_data = cls.check_strip(
                decoded_u_data,
                "GET",
                cls.METHOD_ERR, 
                strip_end=" "
            )

            parsed_data[cls.methodname] = True
            
            # get path
            path = cls.get_substr(
                decoded_u_data,
                " ",
                cls.PATH_ERR
            )

            if path[0] != "/":
                raise Exception(cls.PATH_ERR)
            
            parsed_data[cls.pathname] = path
            decoded_u_data = decoded_u_data.replace(path + " ", "", 1)

            # check http version
            decoded_u_data, http_ver = cls.check_strip_multi(
                decoded_u_data,
                ["HTTP/1.1", "HTTP/1.0"],
                cls.HTTPVER_ERR
            )

            parsed_data[cls.httpvername] = http_ver

            # check line ending for first line in header
            decoded_u_data = cls.check_strip(
                decoded_u_data,
                "\r\n",
                cls.PARSE_ERR
            )

            # get field values (Host, User-Agent, Accept)
            for field in cls.fields:
                decoded_u_data, field_value = cls.get_field(
                    decoded_u_data,
                    field
                )

                if field == "Accept":
                    field_value = field_value.split(",")

                parsed_data[field.upper()] = field_value

            return parsed_data
        
        except Exception as e:
            raise e

    @classmethod
    def get_field(cls, target_str, field, end="\r\n"):
        try:
            error = cls.FIELD_ERR
            target_str = cls.check_strip(
                target_str,
                field + ":",
                error,
                strip_end=" "
            )
            
            field_value = cls.get_substr(
                target_str,
                "\r",
                error
            )

            return target_str.replace(field_value + end, "", 1), field_value

        except Exception as e:
            raise Exception(error + ": " + field)

    @classmethod
    def check_strip(cls, target_str, check_str, error,
        strip_end="", index=0):
        if target_str.find(check_str) != index:
            raise Exception(error)

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

            except Exception as e:
                if count == target_str_len:
                    raise e

    @classmethod
    def get_substr(cls, target_str, end, error):
        substr = ""
        char = ""
        for char in target_str:
            if char == end:
                return substr
            
            substr += char

        raise Exception(error)

# if __name__ == "__main__":
#     request = b"GET / HTTP/1.1\r\nHost: slashdot.org\r\nAccept: python\r\nAgent: text/html\r\n\r\n"
#     parsed_data = HttpReqParser.parse(request)
    
#     for items in parsed_data.items():
#         print(items)