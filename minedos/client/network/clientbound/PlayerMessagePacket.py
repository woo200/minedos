# Copyright (c) John Woo. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import struct
import json

from minedos.client.network import DataTypes
from minedos.client.network.BasePacket import BasePacket
from minedos.client.network.PacketTools import PacketBuilder, PacketReader
from minedos.client.chat import ChatParser


class PlayerMessagePacket(BasePacket):
    def __init__(self, 
                 sender, 
                 index=0, 
                 message_sig_present=False, 
                 message_sig=None,
                 message="",
                 timestamp=0,
                 salt=0,
                 total_prev_messages=0,
                 old_messages=[],
                 unsigned_content_present=False,
                 unsigned_content={},
                 filter_type=0,
                 filter_type_bits=[],
                 chat_type=0,
                 network_name="",
                 network_target_present=False,
                 network_target_name={}) -> None:
        super().__init__(0x35)

        self.sender = sender
        self.index = index
        self.message_sig_present = message_sig_present
        self.message_sig = message_sig
        self.message = message
        self.timestamp = timestamp
        self.salt = salt
        self.total_prev_messages = total_prev_messages
        self.old_messages = old_messages
        self.unsigned_content_present = unsigned_content_present
        self.unsigned_content = unsigned_content
        self.filter_type = filter_type
        self.filter_type_bits = filter_type_bits
        self.chat_type = chat_type
        self.network_name = network_name
        self.network_target_present = network_target_present
        self.network_target_name = network_target_name
    
    def build(self):
        builder = PacketBuilder()

        builder.write_uuid(self.sender)
        builder.write_varint(self.index)
        builder.write_boolean(self.message_sig_present)
        if self.message_sig_present:
            builder.write_bytearray(self.message_sig)
        builder.write_string(self.message)
        builder.write_long(self.timestamp)
        builder.write_long(self.salt)
        builder.write_varint(self.total_prev_messages)
        for message in self.old_messages:
            message_id, signature = message
            builder.write_varint(message_id)
            builder.write_bytearray(signature)
        builder.write_boolean(self.unsigned_content_present)
        if self.unsigned_content_present:
            builder.write_string(json.dumps(self.unsigned_content))
        builder.write_varint(self.filter_type)
        builder.write_bitset(self.filter_type_bits)
        builder.write_varint(self.chat_type)
        builder.write_string(json.dumps(self.network_name))
        builder.write_boolean(self.network_target_present)
        if self.network_target_present:
            builder.write_string(json.dumps(self.network_target_name))

        return builder.get_bytes()

    @staticmethod
    def read(total_length: int, data: bytes):
        reader = PacketReader(data)

        try:
            sender = reader.read_uuid()
            index, _ = reader.read_varint()
            message_sig_present = reader.read_boolean()
            message_sig = None
            if message_sig_present:
                message_sig = reader.read_bytearray()
            message = reader.read_string()
            timestamp = reader.read_long()
            salt = reader.read_long()
            total_prev_messages, _ = reader.read_varint()
            old_messages = []
            for _ in range(total_prev_messages):
                message_id, _ = reader.read_varint()
                signature = reader.read_bytearray()
                old_messages.append((message_id, signature))
            unsigned_content_present = reader.read_boolean()
            unsigned_content = None
            if unsigned_content_present:
                unsigned_content = json.loads(reader.read_string())
            filter_type, _ = reader.read_varint()
            filter_type_bits = []
            if filter_type != 0:
                filter_type_bits = reader.read_bitset()
            chat_type, _ = reader.read_varint()
            network_name = json.loads(reader.read_string())
            network_target_present = reader.read_boolean()
            network_target_name = None
            if network_target_present:
                network_target_name = json.loads(reader.read_string())

        except (ValueError, struct.error, json.JSONDecodeError):
            raise ValueError("Invalid packet data")

        # Check if the packet length is correct
        if not reader.verify_tell(total_length):
            raise ValueError(f"Packet length mismatch (expected {total_length} bytes, got {reader.stream.tell()} bytes)")
        
        return PlayerMessagePacket(sender, 
                                   index, 
                                   message_sig_present, 
                                   message_sig, 
                                   message, 
                                   timestamp, 
                                   salt, 
                                   total_prev_messages, 
                                   old_messages, 
                                   unsigned_content_present, 
                                   unsigned_content, 
                                   filter_type, 
                                   filter_type_bits, 
                                   chat_type, 
                                   network_name, 
                                   network_target_present, 
                                   network_target_name)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(sender={self.sender}, index={self.index}, message_sig_present={self.message_sig_present}, message_sig={self.message_sig}, message={self.message}, timestamp={self.timestamp}, salt={self.salt}, total_prev_messages={self.total_prev_messages}, old_messages={self.old_messages}, unsigned_content_present={self.unsigned_content_present}, unsigned_content={self.unsigned_content}, filter_type={self.filter_type}, filter_type_bits={self.filter_type_bits}, chat_type={self.chat_type}, network_name={self.network_name}, network_target_present={self.network_target_present}, network_target_name={self.network_target_name})"