# Copyright 2020 free5gmano
# All Rights Reserved.
#
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import zipfile
import platform
import shutil
import os
import io
from free5gmano import settings

__system__ = platform.system()
__folder__ = os.getcwd()


def decompression(buffer, templateId, _type):
    response = []
    # Can change template path in settings.py(DATA_DIR)
    directory = os.path.join(settings.DATA_DIR, _type, str(templateId))
    with zipfile.ZipFile(io.BytesIO(buffer)) as zf:
        # printing all the contents of the zip file
        zf.printdir()
        # extracting all the files
        print('Extracting all the files now...')
        zf.extractall(path=directory)
        print('Done!')
        for i in zf.namelist():
            if i[-1] != '/':
                response.append(i)
    return response


def compression(dst_dir: str = 'template_example | template',
                _type: str = "VNF | NSD",
                templateId: str = "<UUID_TYPE>",
                file_name: str = "<Any File>"):
    directory = os.path.join(__folder__, "nssmf", dst_dir, _type, str(templateId), str(file_name))
    os.chdir(directory)
    with zipfile.ZipFile(directory + '.zip', mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        for root, folders, files in os.walk('.'):
            for s_file in files:
                a_file = os.path.join(root, s_file)
                zf.write(a_file)
                # zf.write(a_file, arcname=os.path.join(file_name, a_file))
    os.chdir(__folder__)
    return directory + '.zip'


def del_directory(directory_name):
    directory = os.path.join(__folder__, str(directory_name))
    try:
        shutil.rmtree(directory)
    except OSError as e:
        return e
    else:
        return "success"
