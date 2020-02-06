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

import socket


class CommandOutputSocket(socket.socket):
    def __init__(self):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        bind_ip = "0.0.0.0"
        bind_port = 8888
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind((bind_ip, bind_port))
        self.listen(2)
        self.settimeout(30)
        print("[*] Listening on " + bind_ip + ":" + str(bind_port))
