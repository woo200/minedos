# Copyright (c) John Woo. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import struct
import json

from minedos.client.network import DataTypes
from minedos.client.network.BasePacket import BasePacket
from minedos.client.network.PacketTools import PacketBuilder, PacketReader


class LoginSuccessPacket(BasePacket):
    def __init__(self, uuid, username, properties) -> None:
        super().__init__(0x02)

        self.uuid = uuid
        self.username = username
        self.properties = properties
    
    def build(self):
        builder = PacketBuilder()

        builder.write_uuid(self.uuid)
        builder.write_string(self.username)
        builder.write_array(self.properties)

        return builder.get_bytes()

    @staticmethod
    def read(total_length: int, data: bytes):
        reader = PacketReader(data)

        try:
            uuid = reader.read_uuid()
            username = reader.read_string()
            properties = reader.read_array(DataTypes.Property)
        except (ValueError, struct.error):
            raise ValueError("Invalid packet data")

        # Check if the packet length is correct
        if not reader.verify_tell(total_length):
            raise ValueError(f"Packet length mismatch (expected {total_length} bytes, got {reader.stream.tell()} bytes)")
        
        return LoginSuccessPacket(uuid, username, properties)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(uuid={self.uuid}, username={self.username}, properties={self.properties})"