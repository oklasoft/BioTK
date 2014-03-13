"""
Simple reader for OBO (Open Biomedical Ontology) files.
"""

import collections

import networkx as nx
import pandas as pd

Term = collections.namedtuple("Term", [
    "id", "name", "synonym", "is_a", "part_of", "namespace"
])

def _make_term(attrs):
    if ("id" in attrs) and ("name" in attrs):
        for key in Term._fields:
            attrs.setdefault(key, [])
        return Term(**attrs)

def _parse(handle):
    """
    A simple iterative reader for OBO (Open Biomedical Ontology) files.
    
    :param handle: File handle to the OBO file
    :type handle: A file handle in 'rt' mode

    Currently, only a subset of the OBO specification is supported. 
    Namely, only the following attribute of [Term] entries:
    - id
    - name
    - synonym
    - is_a
    - part_of
    - namespace
    """
    is_term = False
    attrs = collections.defaultdict(list)
    for line in handle:
        line = line.strip()
        if line in ("[Term]", "[Typedef]", "[Instance]"):
            is_term = line == "[Term]"
            t = _make_term(attrs)
            if t and is_term: 
                yield t
            attrs = collections.defaultdict(list)
        elif line:
            try:
                key, value = line.split(": ", 1)
            except ValueError:
                continue

            if key == "id":
                attrs["id"] = value
            elif key == "name":
                attrs["name"] = value
            elif key == "is_a":
                attrs["is_a"].append(value.split("!")[0].strip())
            elif key == "part_of":
                attrs["part_of"].append(value.split("!")[0].strip())
            elif key == "namespace":
                attrs["namespace"] = value
            elif key == "synonym":
                value = value[1:]
                attrs["synonym"].append(value[:value.find("\"")])
    t = _make_term(attrs)
    if t and is_term: 
        yield t

def _parse_as_data_frame(handle):
    terms, synonyms, relations = [], [], []

    for t in _parse(handle):
        terms.append((t.id, t.name, t.namespace))
        for s in t.synonym:
            synonyms.append((t.id, s))
        for target in t.is_a:
            relations.append((t.id, target, "is_a"))

    terms = pd.DataFrame.from_records(terms,
            columns=["Term ID", "Name", "Namespace"],
            index="Term ID")
    synonyms = pd.DataFrame.from_records(synonyms,
            columns=["Term ID", "Synonym"],
            index="Term ID")
    relations = pd.DataFrame.from_records(relations,
            columns=["Agent", "Target", "Relation"])
    return terms, synonyms, relations

class Ontology(object):
    def __init__(self, terms, synonyms, relations):
        self.terms = terms
        self.synonyms = synonyms
        self.relations = relations

    def to_graph(self, relations=["is_a"]):
        g = nx.DiGraph()
        R = self.relations.ix[self.relations["Relation"].isin(relations),:]
        for id,name,ns in self.terms.to_records():
            g.add_node(id, name=name, namespace=ns)
        for id,synonym in self.synonyms.to_records():
            if not "synonyms" in g.node[id]:
                g.node[id]["synonyms"] = []
            g.node[id]["synonyms"].append(synonym)
        for _,agent,target,relation in R.to_records():
            g.add_edge(agent, target, type=relation)
        return g
        
def parse(handle):
    return Ontology(*_parse_as_data_frame(handle))
