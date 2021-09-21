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

import os
from os.path import *

class ResourceLocator:
    index_f = "index.html"

    @classmethod
    def get_filetype(cls, file_descr):
        fname = file_descr.name
        index = len(fname) - 1
        while fname[index] != ".":
            index -= 1

        return fname[index+1:]

    @classmethod
    def find(cls, path, root):
        if path[-1] == "/":
            path += cls.index_f

        full_path = join(root + path)
        # DEBUG CODE:
        # Uncomment to print path information
        # print("path", path)
        # print("full path", full_path)
        # print("root", root)
        # print("abspath full_path", abspath(full_path))
        # print("abspath root", abspath(root))
        # print("root not in abspath full_path", root not in abspath(full_path))

        if abspath(root) not in abspath(full_path):
            return 404, "", None

        try:
            with open(full_path) as file_descr:
                payload = file_descr.read()
                return 200, payload, cls.get_filetype(file_descr)

        except IsADirectoryError:
            path += "/"
            return 301, path, None

        except FileNotFoundError:
            return 404, "", None