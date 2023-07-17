# Copyright (c) John Woo. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from Crypto.Cipher import AES
import os

class AESEncryptedSocket:
    def __init__(self, key, iv, base_socket) -> None:
        self.key = key
        self.iv = iv
        self.base_socket = base_socket

        self.cipher = AES.new(key, AES.MODE_CFB, iv)
        self.r_buffer, self.w_buffer = os.pipe()

    def send(self, data: bytes) -> None:
        data = self.cipher.encrypt(data)
        self.base_socket.send(data)
    
    def sendall(self, data: bytes) -> None:
        data = self.cipher.encrypt(data)
        self.base_socket.sendall(data)
    
    def recv(self, length: int) -> bytes:
        while os.fstat(self.w_buffer).st_size < length:
            data = self.base_socket.recv(1024)
            if not data: # EOF
                break
            os.write(self.w_buffer, self.cipher.decrypt(data))
        return os.read(self.r_buffer, length)
    
    def settimeout(self, timeout: float) -> None:
        self.base_socket.settimeout(timeout)

    def close(self) -> None:
        self.base_socket.close()
        os.close(self.r_buffer)
        os.close(self.w_buffer)
    
    