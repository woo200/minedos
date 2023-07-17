# Copyright (c) John Woo. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import struct
from minedos.client.network import BasePacket
from minedos.client.network import PacketBuilder, PacketReader

class ServerboundLoginStartPacket(BasePacket):
    def __init__(self, username: str, uuid: str = None) -> None:
        super().__init__(0x00)

        self.username = username
        self.uuid = uuid
    
    def build(self):
        builder = PacketBuilder()

        builder.write_string(self.username)
        builder.write_boolean(self.uuid is not None)
        if self.uuid is not None:
            builder.write_uuid(self.uuid)

        return builder.get_bytes()

    @staticmethod
    def read(total_length: int, data: bytes):
        reader = PacketReader(data)

        try:
            username = reader.read_string()
            has_uuid = reader.read_boolean()
            uuid = None
            if has_uuid:
                uuid = reader.read_uuid()
        except (ValueError, struct.error):
            raise ValueError("Invalid packet data")

        # Check if the packet length is correct
        if not reader.verify_tell(total_length):
            raise ValueError(f"Packet length mismatch (expected {total_length} bytes, got {reader.stream.tell()} bytes)")

        return ServerboundLoginStartPacket(username, uuid)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(username={self.username}, uuid={self.uuid})"