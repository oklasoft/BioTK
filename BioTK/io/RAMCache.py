"""
A partial memcache clone in pure Python (both server and client).

Used for semi-persistent function memoization in various parts of BioTK.
"""

# TODO: add a command to clear the cache
# TODO: implement timeouts like in memcache?
# TODO: add a memory limit

import asynchat
import asyncore
import base64
import logging
import os
import pickle
import signal
import socket
import telnetlib
import zlib

log = logging.getLogger(__name__)

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 41313

class Handler(asynchat.async_chat):
    def __init__(self, server, sock, addr):
        super(Handler, self).__init__(sock=sock)
        self._server = server
        self._buffer = []
        self.set_terminator(b"\r\n")

    def collect_incoming_data(self, data):
        self._buffer.append(data)

    def found_terminator(self):
        rs = None
        cmd, *args = self._buffer[0].split()
        if cmd == b"set": 
            if len(self._buffer) == 1:
                try:
                    size = int(args[3])
                except Exception as e:
                    size = 0
                self.set_terminator(size + len(b"\r\n"))
                return
            else:
                data = b"".join(self._buffer[1:]).strip(b"\r\n")
                if cmd == b"set":
                    rs = self.set(args, data)
        elif cmd == b"get":
            rs = self.get(args[0])

        if rs:
            self.push(rs)
        self._buffer = []
        self.set_terminator(b"\r\n")

    def get(self, key):
        try:
            value = self._server._data[key]
            return b"\r\n".join([
                b" ".join([b"VALUE", key, 
                    str(0).encode("ascii"), 
                    str(len(value)).encode("ascii")]),
                value,
                b"END"]) + b"\r\n"
        except KeyError:
            return b"END\r\n"

    def set(self, args, data):
        key = args[0]
        #print(b"setting:", key, data)
        self._server._data[key] = data
        return b"STORED\r\n"

class Server(asyncore.dispatcher):
    """
    A simple memcached server clone.

    Accepts a subset of the memcached protocol:
    - http://blog.elijaa.org/?post/2010/05/21/Memcached-telnet-command-summary

    Inspired by:
    - https://github.com/nmmmnu/MessageQueue/blob/master/some%20tests%20and%20proofs/pymemcached.v.1.py
    """
    
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        super(Server, self).__init__()
        self._data = {}
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host,port))
        self.listen(1)
        self.pid = 0

    def handle_accept(self):
        socket, address = self.accept()
        Handler(self, socket, address)

    def run(self):
        asyncore.loop()

    def fork(self):
        self.pid = os.fork()
        if self.pid == 0:
            self.run()
        else:
            log.info("RAMCache server forked at PID %s" % self.pid)

    def kill(self):
        """
        Kill the forked server (meant to be called from the parent process).
        """
        # I am not sure if I should allow a process to kill itself...
        if self.pid != 0:
            os.kill(self.pid, signal.SIGKILL)

class Client(object):
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self._connection = telnetlib.Telnet(host=host, port=port)

    def _serialize(self, obj):
        return base64.b64encode(zlib.compress(pickle.dumps(obj)))

    def _deserialize(self, data):
        return pickle.loads(zlib.decompress(base64.b64decode(data)))

    def __setitem__(self, key, value):
        assert(isinstance(key, str))
        vstr = self._serialize(value)
        msg = b"set " + key.encode("utf8") + b" 0 0 " \
                + str(len(vstr)).encode("ascii") \
                + b"\r\n" \
                + vstr \
                + b"\r\n"
        self._connection.write(msg)
        self._connection.read_until(b"STORED\r\n")

    def __getitem__(self, key):
        assert(isinstance(key, str))
        key = key.encode("utf8")
        msg = b"get " + key + b"\r\n"
        self._connection.write(msg)
        _,match,_ = self._connection.expect([
            b"VALUE " + key + b" (\d+) (\d+)\r\n"])
        flag = match.group(1)
        bytes = match.group(2)
        # FIXME: ensure data is correct length
        data = self._connection.read_until(b"\r\nEND\r\n")[:-7]
        return self._deserialize(data)

    def __call__(self, fn):
        return self.memoize(fn)

    def memoize(self, fn):
        """
        Wraps a function to memoize the function call with 
        this RAMCacheClient.
        """
        raise NotImplementedError

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", "-p", type=int, default=41313)
    parser.add_argument("--host", "-h", default="0.0.0.0")
    parser.add_argument("--fork", "-f", type=bool, default=False)

    server = Server(host=args.host, port=args.port)
    server.fork()
