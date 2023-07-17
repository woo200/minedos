# Copyright (c) John Woo. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import struct
import uuid
import zlib
import io
from minedos.client.network import DataTypes

class PacketBuilder:
    def __init__(self) -> None:
        self.packet_bytes = io.BytesIO()    
    
    def get_bytes(self) -> None:
        return self.packet_bytes.getvalue()

    def write_varint(self, data: int) -> None:
        self.packet_bytes.write(DataTypes.VarInt.write(data))
    
    def write_string(self, data: str) -> None:
        self.write_varint(len(data))
        self.packet_bytes.write(data.encode("utf-8"))
    
    def write_unsigned_short(self, data: int) -> None:
        self.packet_bytes.write(struct.pack(">H", data))
    
    def write_uuid(self, data: uuid.UUID) -> None:
        self.packet_bytes.write(DataTypes.UUID.write(data))

    def write_bytearray(self, data) -> None:
        self.packet_bytes.write(DataTypes.ByteArray.write(data))
    
    def write_boolean(self, data: bool) -> None:
        self.packet_bytes.write(DataTypes.Boolean.write(data))

    def write_property(self, name, value, signature=None) -> None:
        self.packet_bytes.write(DataTypes.Property.write(name, value, signature))
    
    def write_array(self, data_type, data) -> None:
        self.packet_bytes.write(DataTypes.Array.write(data_type, data))

class PacketReader:
    def __init__(self, data) -> None:
        if isinstance(data, io.BytesIO):
            self.stream = data
        else:
            self.stream = io.BytesIO(data)
    
    def read_varint(self) -> int:
        return DataTypes.VarInt.read(self.stream)
    
    def read_string(self) -> str:
        return DataTypes.String.read(self.stream)
    
    def read_unsigned_short(self) -> int:
        return DataTypes.UnsignedShort.read(self.stream)
    
    def read_boolean(self) -> bool:
        return DataTypes.Boolean.read(self.stream)

    def read_uuid(self) -> uuid.UUID:
        return DataTypes.UUID.read(self.stream)
    
    def read_bytearray(self) -> bytes:
        return DataTypes.ByteArray.read(self.stream)

    def read_property(self) -> tuple:
        return DataTypes.Property.read(self.stream)

    def read_array(self, data_type) -> list:
        return DataTypes.Array.read(self.stream, data_type)

    def verify_tell(self, length: int) -> None:
        return self.stream.tell() == length

    @staticmethod
    def read_packet(socket, compression=None):
        socket.settimeout(5)
        try:
            length, _ = DataTypes.VarInt.read_socket(socket)
            if compression and length > compression:
                data_length, num = DataTypes.VarInt.read_socket(socket)
                data = socket.recv(length - num)
                data = zlib.decompress(data)
                packet_id = data[0]
                data = data[1:]
                return data_length, packet_id, data
            packet_id = socket.recv(1)[0]
            data = socket.recv(length - 1)
            return length, packet_id, data
        except (ValueError, struct.error):
            raise ValueError("Invalid packet data")
            