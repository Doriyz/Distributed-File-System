# Storage Server function:
# 1. Store the file in the local storage
# 2. Communicate with the client to send or receive the file
# 3. Communicate with the other storage servers to replicate the file

import socket
import os
import sys
import time

# Get the hostname and IP address of the storage server
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

