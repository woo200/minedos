# Copyright (c) John Woo. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import socket
import sockslib 
import dns.resolver

import minedos.client.network
import minedos.client.chat

from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_v1_5

class ClientState:
    HANDSHAKE = 0
    STATUS = 1
    LOGIN = 2
    PLAY = 3

class MinecraftClient:
    def __init__(self, *args, **kwargs):
        defaults = {
            "protocol_version": 763,
            "host": None,
            "port": None,
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
        
        self.__resolve_srv_record()
        self.client_state = ClientState.HANDSHAKE

    def __resolve_srv_record(self):
        try:
            answers = dns.resolver.query(f'_minecraft._tcp.{self.arguments["host"]}', 'SRV')
        except dns.resolver.NoAnswer: # No SRV record? Set defaults
            self.real_host = self.arguments['host']
            self.arguments['port'] = 25565
            return
        
        for answer in answers: # SRV record found, if port is set, use that, otherwise use reccomended
            if self.arguments['port'] is None:
                self.arguments['port'] = answer.port
            self.real_host = str(answer.target).rstrip('.')
            return

    def connect(self):
        self.client_socket.connect((self.real_host, self.arguments["port"]))

        handshake_packet = minedos.client.network.serverbound.HandshakePacket(self.arguments["protocol_version"], 
                                                                  self.arguments["host"], 
                                                                  self.arguments["port"], 
                                                                  2) # Send login handshake packet
        self.client_socket.send(handshake_packet.get_bytes())
        self.client_state = ClientState.LOGIN

        login_start_packet = minedos.client.network.serverbound.LoginStartPacket(self.arguments["username"],
                                                                                self.arguments["uuid"])
        self.client_socket.send(login_start_packet.get_bytes())
        
        length, packet_id, data = minedos.client.network.PacketTools.PacketReader.read_packet(self.client_socket)
        encryption_request_packet = minedos.client.network.clientbound.EncryptionRequestPacket.read(length-1, data)

        session_key = get_random_bytes(16)
        cipher = PKCS1_v1_5.new(encryption_request_packet.public_key)

        encrypted_session_key = cipher.encrypt(session_key)
        encrypted_verify_token = cipher.encrypt(encryption_request_packet.verify_token)

        encryption_response_packet = minedos.client.network.serverbound.EncryptionResponsePacket(encrypted_session_key, 
                                                                                                 encrypted_verify_token)
        self.client_socket.send(encryption_response_packet.get_bytes())

        self.client_socket = minedos.client.network.AESEncryptedSocket(session_key, 
                                                                       session_key, 
                                                                       self.client_socket)
        
        length, packet_id, data = minedos.client.network.PacketTools.PacketReader.read_packet(self.client_socket)
        if packet_id == 0x00:
            login_fail_packet = minedos.client.network.clientbound.LoginDisconnectReasonPacket.read(length-1, data)

            print(login_fail_packet.reason)