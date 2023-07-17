# Copyright (c) John Woo. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import struct
import json

from minedos.client.network.BasePacket import BasePacket
from minedos.client.network.PacketTools import PacketBuilder, PacketReader

class EntityPositionUpdatePacket(BasePacket):
    def __init__(self, entity_id, dx, dy, dz, on_ground) -> None:
        super().__init__(0x2B)

        self.entity_id = entity_id
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.on_ground = on_ground
    
    def build(self):
        builder = PacketBuilder()

        builder.write_varint(self.entity_id)
        builder.write_short(self.dx)
        builder.write_short(self.dy)
        builder.write_short(self.dz)
        builder.write_boolean(self.on_ground)

        return builder.get_bytes()

    @staticmethod
    def read(total_length: int, data: bytes):
        reader = PacketReader(data)

        try:
            entity_id, _ = reader.read_varint()
            dx = reader.read_short()
            dy = reader.read_short()
            dz = reader.read_short()
            on_ground = reader.read_boolean()
        except (ValueError, struct.error, json.JSONDecodeError):
            raise ValueError("Invalid packet data")

        # Check if the packet length is correct
        if not reader.verify_tell(total_length):
            raise ValueError(f"Packet length mismatch (expected {total_length} bytes, got {reader.stream.tell()} bytes)")
        
        return EntityPositionUpdatePacket(entity_id, dx, dy, dz, on_ground)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(entity_id={self.entity_id}, dx={self.dx}, dy={self.dy}, dz={self.dz}, on_ground={self.on_ground})"