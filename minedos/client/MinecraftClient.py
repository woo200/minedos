# Copyright (c) John Woo. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import socket
import sockslib 

class MinecraftClient:
    def __init__(self, *args, **kwargs):
        defaults = {
            "protocol_version": 763,
            "host": None,
            "port": 25565,
            "username": None,
            "uuid": None,
            "proxy": None # Dict with keys: proxy_addr, proxy_port(opt), type (opt), ipv6 (opt), auth (opt)
        }
        required = ["host", "username"]

        for arg in required:
            if arg not in kwargs:
                raise ValueError(f"Missing required argument: {arg}")

        self.arguments = {**defaults, **kwargs}

        if self.arguments["proxy"]:
            # Set default proxy values
            proxy_defaults = {
                "proxy_addr": None,
                "proxy_port": 1080,
                "type": sockslib.Socks.SOCKS5,
                "ipv6": False,
                "auth": [sockslib.NoAuth()]
            }
            proxy = {**proxy_defaults, **self.arguments["proxy"]}
            if proxy["proxy_addr"] is None:
                raise ValueError("Missing required argument: proxy_addr")
            
            # Create client socket
            self.client_socket = sockslib.SocksSocket(ip_protocol=socket.AF_INET6 if proxy["ipv6"] else socket.AF_INET)
            self.client_socket.set_proxy((proxy['proxy_addr'], proxy['proxy_port']),
                                         proxy['type'],
                                         proxy['auth'])
        else:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create client socket

    def connect(self):
        self.client_socket.connect((self.arguments["host"], self.arguments["port"]))
