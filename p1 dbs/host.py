import socket
import ssl
import threading
from myDB import myDB
import os

host_ip = '0.0.0.0'
host_port = 9999

# Initialize the database
db = myDB('db.csv')
API_KEY = "1234"


# ssl settings
use_ssl = True
path_to_cert = 'cert.pem'
path_to_key = 'key.pem'


def handle_client(client_socket):
    try:
        client_socket.send('Welcome! Please enter the API key: '.encode('utf-8'))
        user_api_key = client_socket.recv(1024).decode('utf-8')

        #check api key
        if user_api_key != API_KEY:
            client_socket.send('Invalid API key.'.encode('utf-8'))
            return

        client_socket.send('API key accepted. You can now send commands.'.encode('utf-8'))
        
        while True:
            # Receive the request from the client
            request = client_socket.recv(1024).decode('utf-8')
            if not request:
                break

            # Parse the request
            command, *args = request.split()

            if command == 'ADD':
                data = ' '.join(args)
                db.new_entry(data)
                response = 'Item added successfully.'

            elif command == 'UPDATE':
                record_id, new_data = int(args[0]), ' '.join(args[1:])
                try:
                    db.update(record_id, new_data)
                    response = 'Item updated successfully.'
                except ValueError as e:
                    response = str(e)

            elif command == 'REMOVE':
                record_id = int(args[0])
                try:
                    db.delete(record_id)
                    response = 'Item removed successfully.'
                except ValueError as e:
                    response = str(e)

            elif command == 'NUKE':
                db.nuke_db()
                response = 'Database nuked successfully.'

            elif command == 'LIST':
                records = db.select_all()
                if not records:
                    response = 'None'
                else:
                    response = '\n'.join(f"{record['id']}: {record['data']}" for record in records)

            elif command == 'GET_ID':
                record_id = int(args[0])
                record = db.select_by_id(record_id)
                response = f"{record['id']}: {record['data']}" if record else 'Record not found.'

            else:
                response = 'Invalid command.'

            # Send the response back to the client
            client_socket.send(response.encode('utf-8'))
    finally:
        client_socket.close()

def start_server(host=host_ip, port=host_port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f'Server listening on {host}:{port}')

    # if use_ssl switch is set wrap the socket with ssl
    if use_ssl:
        # check if cert.pen and key.pem exist if not create them
        if not os.path.exists(path_to_cert) or not os.path.exists(path_to_key):
            print("Creating cert.pem and key.pem")
            os.system(f"openssl req -x509 -newkey rsa:4096 -keyout {path_to_key} -out {path_to_cert} -days 730 -nodes -subj '/CN=localhost'")

        # wrap the socket with ssl
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=path_to_cert, keyfile=path_to_key)

    while True:
        client_socket, addr = server.accept()
        print(f'Accepted connection from {addr}')
        if use_ssl:
            client_socket = context.wrap_socket(client_socket, server_side=True)
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == '__main__':
    start_server()