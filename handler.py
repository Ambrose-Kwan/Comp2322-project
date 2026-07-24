import os
import socket
import config
import response
import logger


def sanitize_path(path):
    path = path.split('?')[0]
    if path == '/' or path == '':
        path = '/' + config.DEFAULT_PAGE
    if path.startswith('/'):
        path = path[1:]
    if '..' in path or path.startswith('/'):
        return None
    full_path = os.path.join(config.DOC_ROOT, path)
    try:
        full_path = os.path.abspath(full_path)
        doc_root = os.path.abspath(config.DOC_ROOT)
        if not full_path.startswith(doc_root):
            return None
    except Exception:
        return None
    return full_path


def parse_request(request_data):
    try:
        lines = request_data.split('\r\n')
        if not lines:
            return None, None, None, None, None, None
        request_line = lines[0].split()
        if len(request_line) < 3:
            return None, None, None, None, None, None
        method = request_line[0].upper()
        path = request_line[1]
        version = request_line[2].upper()
        headers = {}
        for line in lines[1:]:
            if line == '':
                break
            parts = line.split(':', 1)
            if len(parts) == 2:
                headers[parts[0].strip().lower()] = parts[1].strip()
        connection = headers.get('connection', '').lower()
        if not connection:
            connection = 'keep-alive' if version == 'HTTP/1.1' else 'close'
        if_modified_since = headers.get('if-modified-since')
        request_line_raw = ' '.join(request_line)
        return method, path, version, request_line_raw, if_modified_since, connection
    except Exception:
        return None, None, None, None, None, None


def get_request_filename(path):
    if not path or path == '/':
        return config.DEFAULT_PAGE
    return path.split('?')[0].lstrip('/')


def handle_connection(client_socket, client_address):
    ip_address = client_address[0]
    try:
        buffer = b''
        while True:
            while b'\r\n\r\n' not in buffer:
                chunk = client_socket.recv(4096)
                if not chunk:
                    return
                buffer += chunk
            header_end = buffer.index(b'\r\n\r\n') + 4
            request_bytes = buffer[:header_end]
            buffer = buffer[header_end:]
            try:
                request_str = request_bytes.decode('utf-8')
            except Exception:
                body = response.build_error_body(400)
                headers = response.build_headers(400, 'text/html', len(body), keep_alive=False)
                client_socket.sendall(headers.encode('utf-8') + body)
                logger.log_request(ip_address, 'INVALID', '400 Bad Request')
                return
            method, path, version, request_line, if_modified_since, connection = parse_request(request_str)
            if method is None or version not in ('HTTP/1.0', 'HTTP/1.1'):
                body = response.build_error_body(400)
                headers = response.build_headers(400, 'text/html', len(body), keep_alive=False)
                client_socket.sendall(headers.encode('utf-8') + body)
                logger.log_request(ip_address, 'INVALID', '400 Bad Request')
                print(f'[ERROR] Bad request from {ip_address} -> Sent 400 Bad Request')
                return
            print(f'[THREAD] New connection from {client_address[0]}:{client_address[1]}')
            print("Full HTTP Request:")
            print(request_str)
            print(f'[REQUEST] {request_line}')
            file_path = sanitize_path(path)
            if file_path is None:
                body = response.build_error_body(403)
                headers = response.build_headers(403, 'text/html', len(body), keep_alive=False)
                client_socket.sendall(headers.encode('utf-8') + body)
                logger.log_request(ip_address, get_request_filename(path), '403 Forbidden')
                print(f'[ERROR] Invalid path: {path} -> Sent 403 Forbidden')
                return
            keep_alive_flag = connection == 'keep-alive'
            status_code, status_text, response_data = response.generate_response(method, file_path, if_modified_since, keep_alive=keep_alive_flag)
            client_socket.sendall(response_data)
            requested_file = get_request_filename(path)
            logger.log_request(ip_address, requested_file, f'{status_code} {status_text}')
            print(f'[RESPONSE] Sent {status_code} {status_text} to {ip_address}')
            if not keep_alive_flag:
                return
    except socket.timeout:
        print(f'[TIMEOUT] Connection timed out from {client_address}')
    except Exception as e:
        print(f'Error handling connection from {client_address}: {e}')
    finally:
        try:
            client_socket.close()
        except Exception:
            pass
