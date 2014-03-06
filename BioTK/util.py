def chunks(it, size=1000):
    """
    Divide an iterator into chunks of specified size. A
    chunk size of 0 means no maximum chunk size, and will
    therefore return a single list.
    
    Returns a generator of lists.
    """
    if size == 0:
        yield list(it)
    else:
        chunk = []
        for elem in it:
            chunk.append(elem)
            if len(chunk) == size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk

class ClosingMixin(object):
    """
    Inherit from this mixin class to make a file-like
    object close upon exiting a 'with statement' block.

    Basically does the same thing as :py:func:`contextlib.closing`.
    """

    def __enter__(self):
        return self

    def __exit__(self, *args):
        try:
            self.close()
        except:
            pass
    
    def close(self):
        raise NotImplementedError
