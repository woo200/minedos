# Copyright (c) John Woo. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import socket
import sockslib 
import requests
import dns.resolver

import minedos.client.network
import minedos.client.chat

from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.Hash import SHA1

class ClientState:
    HANDSHAKE = 0
    STATUS = 1
    LOGIN = 2
    PLAY = 3

class MinecraftClient:
    def __init__(self, n_host=None, **kwargs):
        defaults = {
            "protocol_version": 763,
            "host": None,
            "port": None,
            "username": None,
            "uuid": None,
            "proxy": None, # Dict with keys: proxy_addr, proxy_port(opt), type (opt), ipv6 (opt), auth (opt)
            "session_token": None
        }
        required = ["host", "username"]

        if n_host is not None:
            hostport = n_host.split(":")
            if len(hostport) == 1:
                kwargs["host"] = hostport[0]
                kwargs["port"] = 25565
            elif len(hostport) == 2:
                kwargs["host"] = hostport[0]
                kwargs["port"] = int(hostport[1])

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
        self.compression = None

        self.bundled_packets = []

    def __resolve_srv_record(self):
        try:
            answers = dns.resolver.query(f'_minecraft._tcp.{self.arguments["host"]}', 'SRV')
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN): # No SRV record? Set defaults
            self.real_host = self.arguments['host']
            self.arguments['port'] = 25565
            return
        
        for answer in answers: # SRV record found, if port is set, use that, otherwise use reccomended
            if self.arguments['port'] is None:
                self.arguments['port'] = answer.port
            self.real_host = str(answer.target).rstrip('.')
            return
    
    def __handle_disconnect_login(self, length, data):
        login_fail_packet = minedos.client.network.clientbound.LoginDisconnectReasonPacket.read(length-1, data)
        print(login_fail_packet)

    def __handle_set_compression_login(self, length, data):
        set_compression_packet = minedos.client.network.clientbound.SetCompressionPacket.read(length-1, data)
        self.compression = set_compression_packet.threshold
        print(f"Compression set to {self.compression}")
    
    def __handle_encryption_request(self, length, data):
        encryption_request_packet = minedos.client.network.clientbound.EncryptionRequestPacket.read(length-1, data)

        session_key = get_random_bytes(16)
        cipher = PKCS1_v1_5.new(encryption_request_packet.public_key)

        if self.arguments["session_token"] is not None:
            sha1 = SHA1.new()
            sha1.update(encryption_request_packet.server_id.encode('ascii'))
            sha1.update(session_key)
            sha1.update(encryption_request_packet.public_key.exportKey('DER'))
            
            with requests.Session() as session:
                response = session.post("https://sessionserver.mojang.com/session/minecraft/join", 
                                        json={"accessToken": self.arguments["session_token"], 
                                              "selectedProfile": str(self.arguments["uuid"]).replace("-", ""),
                                              "serverId": sha1.hexdigest()})
                response.raise_for_status()

        encrypted_session_key = cipher.encrypt(session_key)
        encrypted_verify_token = cipher.encrypt(encryption_request_packet.verify_token)
        encryption_response_packet = minedos.client.network.serverbound.EncryptionResponsePacket(encrypted_session_key, 
                                                                                                 encrypted_verify_token)
        self.client_socket.send(encryption_response_packet.get_bytes())

        self.client_socket = minedos.client.network.AESEncryptedSocket(session_key, 
                                                                       session_key, 
                                                                       self.client_socket)

    def __handle_login_success(self, length, data):
        login_success_packet = minedos.client.network.clientbound.LoginSuccessPacket.read(length-1, data)
        self.client_state = ClientState.PLAY
        print(f"Logged in as {login_success_packet.username} [{login_success_packet.uuid}]")

    def __handle_system_message(self, length, data):
        system_message_packet = minedos.client.network.clientbound.SystemMessagePacket.read(length-1, data)
        print(system_message_packet.to_chat())
    
    def __handle_player_message(self, length, data):
        try:
            player_message_packet = minedos.client.network.clientbound.PlayerMessagePacket.read(length-1, data)
        except Exception as e:
            e.with_traceback()
            return
        print(player_message_packet)

    def __handle_bundle(self):
        state_play_packet_handlers = {
            0x64: self.__handle_system_message,
            0x35: self.__handle_player_message,
        }
        for packet in self.bundled_packets:
            packet_id, length, data = packet
            if packet_id in state_play_packet_handlers:
                try:
                    state_play_packet_handlers[packet_id](length, data)
                except ValueError:
                    pass

    def __handle_receive_packet(self):
        state_login_packet_handlers = {
            0x00: self.__handle_disconnect_login,
            0x01: self.__handle_encryption_request,
            0x02: self.__handle_login_success,
            0x03: self.__handle_set_compression_login,
        }

        try:
            length, packet_id, data = minedos.client.network.PacketTools.PacketReader.read_packet(self.client_socket, self.compression)
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            return

        if self.client_state == ClientState.LOGIN:
            state_login_packet_handlers[packet_id](length, data)
        if self.client_state == ClientState.PLAY:
            if packet_id != 0x00:
                self.bundled_packets += [(packet_id, length, data)]
            else:
                self.__handle_bundle()
                self.bundled_packets = []


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
        
        while True:
            self.__handle_receive_packet()
