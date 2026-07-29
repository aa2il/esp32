################################################################################
#
# Replacement for micropython's limited urequest library.
# Since the ESP32 has sufficent memory, we use this more "full featured"
# version to get better compatibily with the standard python library.
# The main issue I had with the native mircopython version had to do with
# "chunky" data.
#
# I think this from google AI slop.
#
################################################################################

import usocket

class Response:
    def __init__(self, f):
        self.raw = f
        self.encoding = "utf-8"
        self._cached = None

    def close(self):
        if self.raw:
            self.raw.close()
            self.raw = None
        self._cached = None

    @property
    def content(self):
        if self._cached is None:
            try:
                self._cached = self.raw.read()
            finally:
                self.raw.close()
                self.raw = None
        return self._cached

    @property
    def text(self):
        return str(self.content, self.encoding)

    def json(self):
        import ujson
        return ujson.loads(self.content)

def request(method, url, data=None, json=None, headers={}, stream=None, auth=None, timeout=None):
    if "/" in url:
        scheme, _, host, path = url.split("/", 3)
        path = "/" + path
    else:
        scheme, _, host = url.split("/", 2)
        path = "/"

    if scheme == "http:":
        port = 80
    elif scheme == "https:":
        import ussl
        port = 443
    else:
        raise ValueError("Unsupported scheme")

    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)

    ai = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM)
    ai = ai[0]
    s = usocket.socket(ai[0], ai[1], ai[2])
    
    if timeout is not None:
        s.settimeout(timeout)

    try:
        s.connect(ai[4])
        if scheme == "https:":
            s = ussl.wrap_socket(s, server_hostname=host)
        
        # Send HTTP request headers
        s.write(b"%s %s HTTP/1.1\r\n" % (method.encode(), path.encode()))
        if "Host" not in headers:
            s.write(b"Host: %s\r\n" % host.encode())
        
        for k, v in headers.items():
            s.write(b"%s: %s\r\n" % (k.encode(), v.encode()))
            
        if json is not None:
            import ujson
            data = ujson.dumps(json)
            s.write(b"Content-Type: application/json\r\n")
            
        if data:
            if isinstance(data, str):
                data = data.encode()
            s.write(b"Content-Length: %d\r\n" % len(data))
            s.write(b"\r\n")
            s.write(data)
        else:
            s.write(b"\r\n")

        # Read Response Headers
        f = s.makefile("rwb")
        l = f.readline()
        l = l.split(None, 2)
        status = int(l[1])
        
        chunked = False
        while True:
            l = f.readline()
            if not l or l == b"\r\n":
                break
            if l.lower().startswith(b"transfer-encoding:"):
                if b"chunked" in l.lower():
                    chunked = True

        # Wrap stream if it's chunked to decode it transparently
        if chunked:
            f = ChunkedReader(f)

        resp = Response(f)
        resp.status_code = status
        return resp
    except Exception as e:
        s.close()
        raise e

class ChunkedReader:
    def __init__(self, f):
        self.f = f
        self.chunk_left = 0

    def read(self, sz=-1):
        if sz != -1:
            raise NotImplementedError("Arbitrary chunk sizing is not fully handled here")
        out = bytearray()
        while True:
            if self.chunk_left == 0:
                l = self.f.readline()
                if not l or l == b"\r\n":
                    l = self.f.readline()
                if b";" in l:
                    l = l.split(b";", 1)[0]
                self.chunk_left = int(l.strip(), 16)
                if self.chunk_left == 0:
                    break
            data = self.f.read(self.chunk_left)
            out.extend(data)
            self.chunk_left -= len(data)
        return bytes(out)

    def close(self):
        self.f.close()

def get(url, **kw):
    return request("GET", url, **kw)

def post(url, **kw):
    return request("POST", url, **kw)
