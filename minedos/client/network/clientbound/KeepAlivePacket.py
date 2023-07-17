# Copyright (c) John Woo. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import struct

from minedos.client.network.BasePacket import BasePacket
from minedos.client.network.PacketTools import PacketBuilder, PacketReader


class KeepAlivePacket(BasePacket):
    def __init__(self, keepalive_id) -> None:
        super().__init__(0x23)

        self.keepalive_id = keepalive_id
    
    def build(self):
        builder = PacketBuilder()

        builder.write_long(self.keepalive_id)

        return builder.get_bytes()

    @staticmethod
    def read(total_length: int, data: bytes):
        reader = PacketReader(data)

        try:
            keepalive_id = reader.read_long()
        except (ValueError, struct.error):
            raise ValueError("Invalid packet data")

        # Check if the packet length is correct
        if not reader.verify_tell(total_length):
            raise ValueError(f"Packet length mismatch (expected {total_length} bytes, got {reader.stream.tell()} bytes)")
        
        return KeepAlivePacket(keepalive_id)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(keepalive_id={self.keepalive_id})"