# Copyright (c) John Woo. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import struct
import io

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
    