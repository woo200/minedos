# Copyright (c) John Woo. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import struct
import json

from minedos.client.network import DataTypes
from minedos.client.network.BasePacket import BasePacket
from minedos.client.network.PacketTools import PacketBuilder, PacketReader
from minedos.client.chat import ChatParser


class SystemMessagePacket(BasePacket):
    def __init__(self, content, ovelay) -> None:
        super().__init__(0x64)

        self.content = content
        self.ovelay = ovelay
    
    def build(self):
        builder = PacketBuilder()

        builder.write_string(json.dumps(self.content))
        builder.write_boolean(self.ovelay)

        return builder.get_bytes()

    def to_chat(self):
        return ChatParser.parse(self.content)

    @staticmethod
    def read(total_length: int, data: bytes):
        reader = PacketReader(data)

        try:
            content = json.loads(reader.read_string())
            ovelay = reader.read_boolean()
        except (ValueError, struct.error, json.JSONDecodeError):
            raise ValueError("Invalid packet data")

        # Check if the packet length is correct
        if not reader.verify_tell(total_length):
            raise ValueError(f"Packet length mismatch (expected {total_length} bytes, got {reader.stream.tell()} bytes)")
        
        return SystemMessagePacket(content, ovelay)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(message={self.to_chat()}, ovelay={self.ovelay})"