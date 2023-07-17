# Copyright (c) John Woo. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import minedos
import uuid

client = minedos.MinecraftClient("localhost", 
                                 username="Notch",
                                 uuid=uuid.UUID("069a79f4-44e9-4726-a5be-fca90e38aaf5"),
                                 session_token="")
client.connect()
