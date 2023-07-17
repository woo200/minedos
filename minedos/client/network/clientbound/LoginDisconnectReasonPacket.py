# Copyright (c) John Woo. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import struct
import json

from minedos.client.network.BasePacket import BasePacket
from minedos.client.network.PacketTools import PacketBuilder, PacketReader

class LoginDisconnectReasonPacket(BasePacket):
    def __init__(self, disconnect_reason) -> None:
        super().__init__(0x00)

        self.disconnect_reason = disconnect_reason
    
    def build(self):
        builder = PacketBuilder()

        builder.write_string(json.dumps(self.disconnect_reason))

        return builder.get_bytes()

    @staticmethod
    def read(total_length: int, data: bytes):
        reader = PacketReader(data)

        try:
            disconnect_reason = json.loads(reader.read_string())
        except (ValueError, struct.error, json.JSONDecodeError):
            raise ValueError("Invalid packet data")

        # Check if the packet length is correct
        if not reader.verify_tell(total_length):
            raise ValueError(f"Packet length mismatch (expected {total_length} bytes, got {reader.stream.tell()} bytes)")
        
        return LoginDisconnectReasonPacket(disconnect_reason)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(disconnect_reason={self.disconnect_reason})"