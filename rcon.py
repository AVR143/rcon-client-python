import socket
import struct
import secrets
import select
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class RCONcli:
    def __init__(self, host: str, port: int, password: str):
        self.host = host
        self.port = port
        self.password = password
        self.socket = None

    def __enter__(self):
        self.connect()
        if not self.serverdata_auth():
            raise ConnectionError('Authentication failed!')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
      
    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(10)
        try:
            self.socket.connect((self.host, self.port))
            logging.info("Successful connection to the server.")
        except socket.timeout:
            raise TimeoutError("Connection timed out!")
        except socket.error as e:
            raise ConnectionError(f"Connection error: {e}")

    def disconnect(self):
        if self.socket:
            self.socket.close()
            logging.info("The connection is completed.")

    def create_packet(self, packet_type, body):
        request_id = secrets.randbelow(2147483647) + 1
        packet_body = body.encode('utf-8')
        packet_size = 10 + len(packet_body)
        packet = struct.pack('<3i', packet_size, request_id, packet_type) + packet_body + b'\x00\x00'
        return packet

    def receive_packet(self):
        ready = select.select([self.socket], [], [], 10)
        if ready[0]:
            response = self.socket.recv(4096)
            if len(response) < 12:
                raise ConnectionError("An incomplete or damaged package was received from the server.")
            response_size, request_id, packet_type = struct.unpack('<3i', response[:12])
            body = response[12:response_size + 4].decode('utf-8').strip().strip('\x00')
            return {'size': response_size,
                    'request_id': request_id,
                    'type': packet_type,
                    'body': body}
        else:
            raise TimeoutError("A response from the server was not received within 10 seconds "
                            "and the connection was terminated.")

    def serverdata_auth(self):
        if self.socket:
            packet = self.create_packet(3, self.password)
            self.socket.send(packet)
            response = self.receive_packet()
            if response['request_id'] == -1:
                raise ValueError("Incorrect password")
            logging.info('Authorization was successful!')
            return True
        return False

    def send_command(self, command):
        if self.socket:
            packet = self.create_packet(2, command)
            self.socket.send(packet)
            response = self.receive_packet()
          
            # Sometimes after sending a command, the server may send a Type 2 packet with an empty body
            # Checking that the response was Type 0 in order to successfully display the result of the command
            retries = 0
            while response and response['type'] == 2 and not response['body'] and retries < 3:
                logging.warning(f"Received empty response (type 2). Retrying ({retries + 1}/3)...")
                response = self.receive_packet()
                retries += 1
              
            if retries >= 3:
                raise Exception("Server is not responding properly.")
            logging.info(f"Server response: {response['body']}")

# Usage example
if __name__ == "__main__":
    try:
        with RCONcli('127.0.0.1', 27015, '12345') as rcon_client:
            rcon_client.send_command('players')
    except Exception as e:
        raise Exception(f"An error occurred: {e}")
