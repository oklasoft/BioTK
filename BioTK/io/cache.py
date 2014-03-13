"""
Cache downloads or computation results in RAM or on the filesystem.
"""

import base64
import hashlib
import logging
import os
import pickle
import urllib.request

import memcache

import BioTK.config

log = logging.getLogger(__name__)

MEMCACHED_SLAB_SIZE = 1024 * 512

def memcached(host="127.0.0.1", port=11211):
    client = memcache.Client(["%s:%s" % (host,port)], debug=0)
    def decorator(fn):
        def wrapped(*args, **kwargs):
            key_data = (fn.__module__ + fn.__name__ + str(args))\
                    .encode("utf-8")
            key_base = hashlib.md5(key_data).hexdigest()
            slabs = client.get(key_base)

            if slabs is None:
                result = fn(*args, **kwargs)
                s = pickle.dumps(result)
                slabs = 0
                for i in range(0, len(s), MEMCACHED_SLAB_SIZE):
                    key = key_base + "-" + str(i // MEMCACHED_SLAB_SIZE)
                    data = s[i:min(i+MEMCACHED_SLAB_SIZE, len(s))]
                    client.set(key, data)
                client.set(key_base, len(s) // MEMCACHED_SLAB_SIZE)
            else:
                data = b"".join(client.get(key_base+"-"+str(i)) 
                        for i in range(slabs+1))
                result = pickle.loads(data)
            return result

        return wrapped
    return decorator

RAMCache = memcached

# TODO: actually use cache_size (in MB) and make this FIFO 

def download(url):
    dest = os.path.join(BioTK.config.CACHE_DIR.encode("utf-8"), 
            base64.b64encode(url.encode("utf-8")))
    
    if not os.path.exists(dest):
        log.info("Cache miss for URL: %s" % url)
        urllib.request.urlretrieve(url, dest)

    return dest
