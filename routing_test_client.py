import socket
import threading
import sys

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                print("Server Disconnected.")
                sys.exit()
            print(f"\nServer : {message}")
        except Exception as e:
            print(f"Recv Error : {e}")
            sys.exit()

def send_messages(client_socket):
    while True:
        try:
            message = input("\nInput Your Message : ")
            client_socket.sendall(message.encode('utf-8'))
        except Exception as e:
            print(f"Send Error : {e}")
            sys.exit()
            

def start_tcp_client(host='localhost', port=12345):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    send_thread = threading.Thread(target=send_messages, args=(client_socket,))
    
    receive_thread.start()
    send_thread.start()
    
    receive_thread.join()
    send_thread.join()
    
    client_socket.close()

# 클라이언트 시작
start_tcp_client()