# Copyright (c) John Woo. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from minedos.client.network import DataTypes
import zlib

class BasePacket:
    def __init__(self, packet_id: int) -> None:
        self.packet_id = packet_id
        self.compression = None
    
    def set_compression(self, compression=None):
        self.compression = compression

    def get_bytes(self) -> None:
        data = bytes([self.packet_id]) + self.build()
    
        if self.compression != None:
            if len(data) > self.compression:
                d_len = len(data)
                data = zlib.compress(data)
                data_length = DataTypes.VarInt.write(d_len)
                packet_length = DataTypes.VarInt.write(len(data) + len(data_length))
                return packet_length + data_length + data
            data = DataTypes.VarInt.write(0) + data
        
        return DataTypes.VarInt.write(len(data)) + data
    
    def build(self) -> None:
        return None

    @staticmethod
    def read(total_length: int, data: bytes): # -> BasePacket instance
        raise NotImplementedError("This method must be implemented in a subclass")

    def __repr__(self) -> str:
        return f"{type(self).__name__}(packet_id={self.packet_id})"