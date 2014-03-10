"""
Event and relation extraction.
"""

import gzip
import json
import sys
import fileinput

import networkx as nx

def main(handle):
    for line in handle:
        sentences = json.loads(line)
        for sentence in sentences:
            g = nx.DiGraph()
            for i,(w,t) in enumerate(zip(sentence["words"], sentence["tags"])):
                g.add_node(i, word=w, tag=t)
            for gov,dep,type in sentence["edges"]:
                g.add_edge(dep, gov, type=type)

if __name__ == "__main__":
    handle = fileinput.input()
    main(handle)
