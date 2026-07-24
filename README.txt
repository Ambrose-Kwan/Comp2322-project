COMP 2322 - Multi-threaded Web Server
======================================

Project Overview
------------
This project is a multi-threaded Web Server implemented in Python using the socket API. 
It supports concurrent client connections and handles HTTP/1.1 GET and HEAD requests, conditional GETs, and persistent connections.

Requirements
------------
- Python 3.6 or above

Files Description
-----
server.py   - Main server: creates listening socket, spawns a thread per connection
handler.py  - Per-connection logic: parses HTTP requests and dispatches responses
response.py - Builds HTTP response headers and bodies for all status codes
logger.py   - Thread-safe access log writer
config.py   - Configuration (host, port, doc root, log path, default page)
client.py   - Simple interactive HTTP client for testing
public/     - Document root served by the server
  index.html  - Default HTML page
  test.png    - Test image file (for image GET testing)
  test.jpg    - Test image file (for image GET testing)
access_log.txt - Access log (auto-created/appended on first request)

How to Run the Server
---------------------
1. Open a terminal/PowerShell.
2. Run:
       python server.py

   The server listens on 127.0.0.1:8000 by default.
   Press Ctrl+C to stop the server.
3. Testing via Browser:
    Open your web browser and visit:
  - **HTML Test:** `http://127.0.0.1:8000/index.html`
  - **Image Test:** `http://127.0.0.1:8000/test.png`
4. Testing Status Codes via Terminal (curl)
  To verify specific HTTP behaviors, run these commands in a second terminal:
  - **200 OK (HEAD):** `curl.exe -v http:// 127.0.0.1:8000/index.html`
  - **404 Not Found:** `curl.exe -v http://127.0.0.1:8000/this_is_not_here.html`
  - **403 Forbidden (Directory Traversal):** `curl.exe - - path-as-if -v http://127.0.0.1:8000/../server.py`
  - **304 Not Modified:** `curl.exe -v -H "If-Modified-Since: Fri, 01 Jan 2027 00:00:00 GMT" http://127.0.0.1:8000/index.html`
  - **400 Bad Request:**
  Use `python client.py` and input an invalid string like `BAD_REQUEST_STRING` then press Enter twice.

How to Run the Client
---------------------
Open a second terminal in the project directory and run:
       python client.py

Then type an HTTP request at the prompt, for example:

  GET /index.html HTTP/1.1
  Host: 127.0.0.1

  (press Enter twice to send)

Sample Requests for Testing Every Feature
------------------------------------------
# 200 OK - serve HTML file
GET /index.html HTTP/1.1

# 200 OK - serve image file
GET /test.png HTTP/1.1

# HEAD command
HEAD /index.html HTTP/1.1

# 404 File Not Found
GET /missing.html HTTP/1.1

# 400 Bad Request (unsupported method)
POST /index.html HTTP/1.1

# 304 Not Modified (replace <date> with Last-Modified value from a prior response)
GET /index.html HTTP/1.1
If-Modified-Since: <date>

# Persistent connection (keep-alive)
GET /index.html HTTP/1.1
Connection: keep-alive

# Non-persistent connection (close)
GET /index.html HTTP/1.1
Connection: close

Configuration
-------------
Edit config.py to change:
  HOST        - listening address (default: 127.0.0.1)
  PORT        - listening port    (default: 8000)
  DOC_ROOT    - document root     (default: ./public)
  LOG_FILE    - access log path   (default: ./access_log.txt)
  DEFAULT_PAGE- default page      (default: index.html)

Log Format
----------
All requests are automatically logged into `access_log.txt` in the root directory following the format: `[IP, Timestamp, Filename, Status]`.
Each line in access_log.txt:
  <client IP>, <timestamp>, <requested file>, <status code and text>

Example:
  127.0.0.1, 2026-04-07 10:00:00, index.html, 200 OK