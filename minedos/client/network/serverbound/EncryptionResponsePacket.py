# Copyright (c) John Woo. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import struct
from minedos.client.network.BasePacket import BasePacket
from minedos.client.network.PacketTools import PacketBuilder, PacketReader

class EncryptionResponsePacket(BasePacket):
    def __init__(self, shared_secret: bytes, verify_token: bytes) -> None:
        super().__init__(0x01)

        self.shared_secret = shared_secret
        self.verify_token = verify_token
    
    def build(self):
        builder = PacketBuilder()

        builder.write_bytearray(self.shared_secret)
        builder.write_bytearray(self.verify_token)

        return builder.get_bytes()

    @staticmethod
    def read(total_length: int, data: bytes):
        reader = PacketReader(data)

        try:
            shared_secret = reader.read_bytearray()
            verify_token = reader.read_bytearray()
        except (ValueError, struct.error):
            raise ValueError("Invalid packet data")

        # Check if the packet length is correct
        if not reader.verify_tell(total_length):
            raise ValueError(f"Packet length mismatch (expected {total_length} bytes, got {reader.stream.tell()} bytes)")

        return EncryptionResponsePacket(shared_secret, verify_token)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(shared_secret={self.shared_secret}, verify_token={self.verify_token})"