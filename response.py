import os
import time
from email.utils import formatdate
import config


STATUS_PHRASES = {
    200: 'OK',
    400: 'Bad Request',
    403: 'Forbidden',
    404: 'File Not Found',
    304: 'Not Modified',
}


CONTENT_TYPES = {
    '.html': 'text/html',
    '.htm': 'text/html',
    '.txt': 'text/plain',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.css': 'text/css',
    '.js': 'application/javascript',
}


def get_content_type(file_path):
    return CONTENT_TYPES.get(os.path.splitext(file_path)[1].lower(), 'application/octet-stream')


def parse_http_date(date_string):
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_string).timestamp()
    except Exception:
        return None


def get_last_modified(file_path):
    try:
        return formatdate(timeval=os.path.getmtime(file_path), usegmt=True)
    except Exception:
        return None


def build_error_body(status_code):
    reason = STATUS_PHRASES.get(status_code, 'Error')
    if status_code == 400:
        message = 'The server could not understand the request due to invalid syntax.'
    elif status_code == 403:
        message = 'Forbidden'
    elif status_code == 404:
        message = 'File Not Found'
    else:
        message = 'An error occurred while processing your request.'

    body = (
        '<!DOCTYPE html>\n'
        '<html lang="en">\n'
        '<head><meta charset="UTF-8"><title>{code} {reason}</title></head>\n'
        '<body>\n'
        '<h1>{code} {reason}</h1>\n'
        f'<p>{message}</p>\n'
        '</body>\n'
        '</html>\n'
    ).replace('{code}', str(status_code)).replace('{reason}', reason)
    return body.encode('utf-8')


def build_headers(status_code, content_type, content_length, last_modified=None, keep_alive=False):
    status_line = f'HTTP/1.1 {status_code} {STATUS_PHRASES.get(status_code, "OK")}\r\n'
    headers = [
        f'Content-Type: {content_type}',
        f'Content-Length: {content_length}',
    ]
    if last_modified:
        headers.append(f'Last-Modified: {last_modified}')
    headers.append('Connection: keep-alive' if keep_alive else 'Connection: close')
    return status_line + '\r\n'.join(headers) + '\r\n\r\n'


def generate_response(method, file_path, if_modified_since=None, keep_alive=False):
    if method not in ['GET', 'HEAD']:
        body = build_error_body(400)
        headers = build_headers(400, 'text/html', len(body), keep_alive=False)
        return 400, STATUS_PHRASES[400], headers.encode('utf-8') + body

    if not file_path or not os.path.exists(file_path):
        body = build_error_body(404)
        headers = build_headers(404, 'text/html', len(body), keep_alive=keep_alive)
        return 404, STATUS_PHRASES[404], headers.encode('utf-8') + body

    if not os.path.isfile(file_path) or not os.access(file_path, os.R_OK):
        body = build_error_body(403)
        headers = build_headers(403, 'text/html', len(body), keep_alive=keep_alive)
        return 403, STATUS_PHRASES[403], headers.encode('utf-8') + body

    try:
        file_mtime = os.path.getmtime(file_path)
    except Exception:
        body = build_error_body(403)
        headers = build_headers(403, 'text/html', len(body), keep_alive=keep_alive)
        return 403, STATUS_PHRASES[403], headers.encode('utf-8') + body

    if if_modified_since:
        client_time = parse_http_date(if_modified_since)
        if client_time is not None and file_mtime <= client_time:
            headers = build_headers(304, 'text/plain', 0, keep_alive=keep_alive)
            return 304, STATUS_PHRASES[304], headers.encode('utf-8')

    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()
    except Exception:
        body = build_error_body(403)
        headers = build_headers(403, 'text/html', len(body), keep_alive=keep_alive)
        return 403, STATUS_PHRASES[403], headers.encode('utf-8') + body

    headers = build_headers(200, get_content_type(file_path), len(file_content), get_last_modified(file_path), keep_alive=keep_alive)
    if method == 'HEAD':
        return 200, STATUS_PHRASES[200], headers.encode('utf-8')
    return 200, STATUS_PHRASES[200], headers.encode('utf-8') + file_content