# RCON Client
This project provides a simple client to connect to a server via RCON (Remote Console) using Python. It allows you to authenticate, send commands and receive responses from the server.

# Installation
To use this client, make sure you have Python 3.x installed.
1. Download or clone the repository.
2. Make sure that all dependencies are installed (in this case, no additional dependencies are required).

# Usage
To use the client, you need to provide a host, port, and password to connect to the server.
Usage example:
```python
from rcon import RCONcli

with RCONcli(host='127.0.0.1', port=27015, password='12345') as rcon_client:
    rcon_client.send_command('players')
```
Console output:
```txt
[INFO] Successful connection to the server.
[INFO] Authorization was successful!
[INFO] Server response: Players connected (1): 
-AVR
[INFO] The connection is completed.
```

# Description of classes and methods
`RCONcli` class:
- `__init__(host: str, port: int, password: str)` — Initializes the client with the specified parameters for connecting to the server.
- `__enter__()` — Method for use with the `with` context manager. Connects the client and authenticates the user.
- `__exit__(exc_type, exc_val, exc_tb)` — Method for gracefully ending work `with` context manager (closes the connection).
- `connect()` — Establishes a TCP connection to the server.
- `disconnect()` — Closes the TCP connection.
- `create_packet(packet_type, body)` — Creates and forms a packet to send to the server.
- `receive_packet()` — Receives and decrypts the response from the server.
- `serverdata_auth()` — Performs authentication on the server.
- `send_command(command)` — Sends a command to the server and receives a response.

# Error handling
- `TimeoutError` - If the connection is not established within 10 seconds or the server does not respond within 10 seconds.
- `ConnectionError` - If a connection error occurred while establishing a connection.
- `ValueError` - If an incorrect password was entered during authentication.

Logging is configured via the standard `logging` module. All important events (such as successful connection, errors, and responses from the server) will be displayed in the console.
