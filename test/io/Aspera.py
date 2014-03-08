from BioTK.io import Aspera

def test():
    import hashlib
    import gzip

    if False:
        client = Aspera.Client()
        path = "/geo/README.txt"
        expected_md5 = "e71689d0f875b1641f043e167904f65e"

        with client.download(path) as h:
            md5 = hashlib.md5()
            while True:
                s = h.read(1024)
                if not s:
                    break
                md5.update(s)
            digest = md5.hexdigest()
            assert(digest == expected_md5)
