# Copyright (c) John Woo. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import struct
import json

from minedos.client.network.BasePacket import BasePacket
from minedos.client.network.PacketTools import PacketBuilder, PacketReader

class SetCompressionPacket(BasePacket):
    def __init__(self, threshold) -> None:
        super().__init__(0x03)

        self.threshold = threshold
    
    def build(self):
        builder = PacketBuilder()

        builder.write_varint(self.threshold)

        return builder.get_bytes()

    @staticmethod
    def read(total_length: int, data: bytes):
        reader = PacketReader(data)

        try:
            threshold, _ = reader.read_varint()
        except (ValueError, struct.error, json.JSONDecodeError):
            raise ValueError("Invalid packet data")

        # Check if the packet length is correct
        if not reader.verify_tell(total_length):
            raise ValueError(f"Packet length mismatch (expected {total_length} bytes, got {reader.stream.tell()} bytes)")
        
        return SetCompressionPacket(threshold)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(threshold={self.threshold})"