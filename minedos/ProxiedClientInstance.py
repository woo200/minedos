# Copyright (c) John Woo. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import sockslib
import socket

class ProxiedClientInstance:
    def create(self, *args, **kwargs) -> None:
        defaults = {
            'proxy_addr': None,
            'proxy_port': 1080,
            'proxy_type': sockslib.Socks.SOCKS5,
            'proxy_ipv6': False,
            'proxy_auth': [sockslib.NoAuth()],
            'properties': None,
        }

        self.arguments = {**defaults, **kwargs}

        self.properties = self.arguments['properties']
        self.proxy_addr = self.arguments['proxy_addr']
        self.proxy_port = self.arguments['proxy_port']
        self.proxy_type = self.arguments['proxy_type']
        self.proxy_auth = self.arguments['proxy_auth']
        self.proxy_inet = socket.AF_INET6 if self.arguments['proxy_ipv6'] else socket.AF_INET

        sockslib.set_default_proxy((self.proxy_addr, self.proxy_port), 
                                   self.proxy_type, 
                                   self.proxy_inet, 
                                   self.proxy_auth)
        old_socket = socket.socket
        socket.socket = sockslib.SocksSocket

        self.bot = mineflayer.createBot(self.properties)

        socket.socket = old_socket