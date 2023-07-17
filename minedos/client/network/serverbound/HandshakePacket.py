# Copyright (c) John Woo. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import struct
from minedos.client.network import BasePacket
from minedos.client.network import PacketBuilder, PacketReader

class HandshakePacket(BasePacket):
    def __init__(self, protocol_version: int, server_address: str, server_port: int, next_state: int) -> None:
        super().__init__(0x00)

        self.protocol_version = protocol_version
        self.server_address = server_address
        self.server_port = server_port
        self.next_state = next_state
    
    def build(self):
        builder = PacketBuilder()

        builder.write_varint(self.protocol_version)
        builder.write_string(self.server_address)
        builder.write_unsigned_short(self.server_port)
        builder.write_varint(self.next_state)

        return builder.get_bytes()

    @staticmethod
    def read(total_length: int, data: bytes):
        reader = PacketReader(data)

        try:
            protocol_version, _ = reader.read_varint()
            server_address = reader.read_string()
            server_port = reader.read_unsigned_short()
            next_state, _ = reader.read_varint()
        except (ValueError, struct.error):
            raise ValueError("Invalid packet data")

        # Check if the packet length is correct
        if not reader.verify_tell(total_length):
            raise ValueError(f"Packet length mismatch (expected {total_length} bytes, got {reader.stream.tell()} bytes)")

        return HandshakePacket(protocol_version, server_address, server_port, next_state)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(protocol_version={self.protocol_version}, server_address={self.server_address}, server_port={self.server_port}, next_state={self.next_state})"