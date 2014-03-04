from BioTK.genome import Region

def parse(handle):
    keys = ["contig", "start", "end", "name", "score", "strand"]

    for line in handle:
        fields = line.strip().split("\t")
        attrs = dict(zip(keys, fields))
        attrs["start"] = int(attrs["start"])
        attrs["end"] = int(attrs["end"])
        if "score" in attrs:
            attrs["score"] = float(attrs["score"])
        yield Region(**attrs)
