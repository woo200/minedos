# Copyright (c) John Woo. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import struct

from minedos.client.network.BasePacket import BasePacket
from minedos.client.network.PacketTools import PacketBuilder, PacketReader


class PlayerMessagePacket(BasePacket):
    def __init__(self, message, timestamp, salt, has_signature, signature, message_count, acknowleged) -> None:
        super().__init__(0x05)

        self.message = message
        self.timestamp = timestamp
        self.salt = salt
        self.has_signature = has_signature
        self.signature = signature
        self.message_count = message_count
        self.acknowleged = acknowleged
    
    def build(self):
        builder = PacketBuilder()
 	
        builder.write_string(self.message)
        builder.write_long(self.timestamp)
        builder.write_long(self.salt)
        builder.write_boolean(self.has_signature)
        if self.has_signature:
            builder.write_bytearray(self.signature)
        builder.write_varint(self.message_count)
        builder.write_bitset(self.acknowleged)

        return builder.get_bytes()

    @staticmethod
    def read(total_length: int, data: bytes):
        reader = PacketReader(data)

        try:
            message = reader.read_string()
            timestamp = reader.read_long()
            salt = reader.read_long()
            has_signature = reader.read_boolean()
            signature = None
            if has_signature:
                signature = reader.read_bytearray()
            message_count = reader.read_varint()
            acknowleged = reader.read_bitset()
        except (ValueError, struct.error):
            raise ValueError("Invalid packet data")

        # Check if the packet length is correct
        if not reader.verify_tell(total_length):
            raise ValueError(f"Packet length mismatch (expected {total_length} bytes, got {reader.stream.tell()} bytes)")
        
        return PlayerMessagePacket(message, timestamp, salt, has_signature, signature, message_count, acknowleged)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(message={self.message}, timestamp={self.timestamp}, salt={self.salt}, has_signature={self.has_signature}, signature={self.signature}, message_count={self.message_count}, acknowleged={self.acknowleged})"