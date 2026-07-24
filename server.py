import socket
import threading
import config
import handler

def main():
    
    # Create socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # SET SERVER TIMEOUT (1.0 second)
    server_socket.settimeout(1.0)

    try:

        server_socket.bind((config.HOST, config.PORT))
        
        # Listen for incoming connections (queue size of 5)
        server_socket.listen(5)
        
        print(f"Server started on {config.HOST}:{config.PORT}...")
        print("Press Ctrl+C to stop the server...\n")
        
        # Main connection loop
        while True:
            try:
                # Accept incoming connection
                # This will now only block for 1 second due to settimeout(1.0)
                client_socket, client_address = server_socket.accept()
                print(f"[Connection] {client_address[0]}:{client_address[1]}")
                
                # Threading
                client_socket.settimeout(15.0)
                thread = threading.Thread(
                    target=handler.handle_connection,
                    args=(client_socket, client_address)
                )
                thread.daemon = True  # Daemon thread: exits when main program exits
                thread.start()
                
            except socket.timeout:
                continue

            except Exception as e:
                print(f"Error accepting connection: {e}")
                continue
    
    except OSError as e:
        print(f"Error binding socket: {e}")

    except KeyboardInterrupt:
        print("\n\nShutting down server...")
    
    finally:
        try:
            server_socket.close()
            print("Server socket closed.")
        except:
            pass

if __name__ == '__main__':
    main()