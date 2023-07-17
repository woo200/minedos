# Copyright (c) John Woo. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import struct
from minedos.client.network import DataTypes

class BasePacket:
    def __init__(self, packet_id: int) -> None:
        self.packet_id = packet_id
    
    def get_bytes(self) -> None:
        data = bytes([self.packet_id]) + self.build()
        return DataTypes.VarInt.write(len(data)) + data
    
    def build(self) -> None:
        return None

    @staticmethod
    def read(total_length: int, data: bytes): # -> BasePacket instance
        return None

    def __repr__(self) -> str:
        return f"{type(self).__name__}(packet_id={self.packet_id})"