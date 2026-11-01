"""A client that promises 100 bytes, sends 10, and hangs up. The decision never gets its body."""
import socket
import time

with socket.create_connection(("localhost", 10000)) as s:
    s.sendall(b"POST /orders HTTP/1.1\r\nhost: localhost\r\ncontent-length: 100\r\n\r\n" + b"x" * 10)
    time.sleep(0.5)
print("sent 10 of 100 bytes, hung up")
