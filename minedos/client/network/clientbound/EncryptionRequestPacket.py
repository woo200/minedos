# Copyright (c) John Woo. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import struct
from minedos.client.network.BasePacket import BasePacket
from minedos.client.network.PacketTools import PacketBuilder, PacketReader

class EncryptionRequestPacket(BasePacket):
    def __init__(self, public_key, verify_token, server_id: str = "") -> None:
        super().__init__(0x01)

        self.public_key = public_key
        self.verify_token = verify_token
        self.server_id = server_id
    
    def build(self):
        builder = PacketBuilder()

        builder.write_string(self.server_id)
        builder.write_bytearray(self.public_key)
        builder.write_bytearray(self.verify_token)

        return builder.get_bytes()

    @staticmethod
    def read(total_length: int, data: bytes):
        reader = PacketReader(data)

        try:
            server_id = reader.read_string()
            public_key = reader.read_bytearray()
            verify_token = reader.read_bytearray()
        except (ValueError, struct.error):
            raise ValueError("Invalid packet data")

        # Check if the packet length is correct
        if not reader.verify_tell(total_length):
            raise ValueError(f"Packet length mismatch (expected {total_length} bytes, got {reader.stream.tell()} bytes)")

        return EncryptionRequestPacket(public_key, verify_token, server_id)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(server_id={self.server_id}, public_key={self.public_key}, verify_token={self.verify_token})"