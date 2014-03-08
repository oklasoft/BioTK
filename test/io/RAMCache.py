from BioTK.io.RAMCache import Client, Server

def test():
    s = Server()
    s.fork()

    c = Client()
    c["abc"] = "def"
    assert(c["abc"] == "def")

    c["foo"] = 1234
    assert(c["foo"] == 1234)

    s.kill()
