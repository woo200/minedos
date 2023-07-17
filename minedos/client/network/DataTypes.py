# Copyright (c) John Woo. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import struct
import uuid

class VarInt:
    @staticmethod
    def write(data) -> bytes:
        result = b""
        while True:
            byte = data & 0x7F
            data >>= 7
            if data != 0:
                byte |= 0x80
            result += struct.pack("B", byte)
            if data == 0:
                break
        return result
    
    @staticmethod
    def read(stream):
        num_read = 0
        result = 0
        while True:
            read = stream.read(1)
            if len(read) == 0:
                raise ValueError("Reached EOF")
            read = read[0]
            value = read & 0x7F
            result |= (value << (7 * num_read))
            num_read += 1
            if num_read > 5:
                raise ValueError("VarInt is too big")
            if (read & 0x80) != 128:
                break
        return result, num_read

    @staticmethod
    def read_socket(socket):
        num_read = 0
        result = 0
        while True:
            read = socket.recv(1)
            if len(read) == 0:
                raise ValueError("Reached EOF")
            read = read[0]
            value = read & 0x7F
            result |= (value << (7 * num_read))
            num_read += 1
            if num_read > 5:
                raise ValueError("VarInt is too big")
            if (read & 0x80) != 128:
                break
        return result, num_read

class String:
    @staticmethod
    def write(data: str) -> bytes:
        return VarInt.write(len(data)) + data.encode("utf-8")

    @staticmethod
    def read(stream) -> str:
        length, _ = VarInt.read(stream)
        return stream.read(length).decode("utf-8")

class UnsignedShort:
    @staticmethod
    def write(data: int) -> bytes:
        return struct.pack(">H", data)
    
    @staticmethod
    def read(stream) -> int:
        return struct.unpack(">H", stream.read(2))[0]
    
class Boolean:
    @staticmethod
    def write(data: bool) -> bytes:
        return struct.pack("?", data)
    
    @staticmethod
    def read(stream) -> bool:
        return struct.unpack("?", stream.read(1))[0]

class UUID:
    @staticmethod
    def write(data: uuid.UUID) -> bytes:
        return struct.pack(">QQ", data.int >> 64, data.int & (2 ** 64 - 1))
    
    @staticmethod
    def read(stream) -> uuid.UUID:
        return uuid.UUID(bytes=stream.read(16))

class ByteArray:
    @staticmethod
    def write(data: bytes) -> bytes:
        return VarInt.write(len(data)) + data
    
    @staticmethod
    def read(stream) -> bytes:
        length, _ = VarInt.read(stream)
        return stream.read(length)

class Property:
    @staticmethod
    def write(data) -> bytes:
        name, value, signature = data

        data = String.write(name) + String.write(value)
        if signature is not None:
            data += Boolean.write(True) + String.write(signature)
        else:
            data += Boolean.write(False)
        return data

    @staticmethod
    def read(stream):
        name = String.read(stream)
        value = String.read(stream)
        has_signature = Boolean.read(stream)
        if has_signature:
            signature = String.read(stream)
        else:
            signature = None
        return name, value, signature

class Array:
    @staticmethod
    def read(stream, data_type):
        length, _ = VarInt.read(stream)
        return [data_type.read(stream) for _ in range(length)]
    
    @staticmethod
    def write(data, data_type):
        return VarInt.write(len(data)) + b"".join([data_type.write(d) for d in data])

class Long:
    @staticmethod
    def write(data: int) -> bytes:
        return struct.pack(">q", data)
    
    @staticmethod
    def read(stream) -> int:
        return struct.unpack(">q", stream.read(8))[0]

class BitSet:
    @staticmethod
    def write(data: list) -> bytes:
        return VarInt.write(len(data)) + b"".join([Long.write(d) for d in data])
    
    @staticmethod
    def read(stream) -> list:
        length, _ = VarInt.read(stream)
        return [Long.read(stream) for _ in range(length)]