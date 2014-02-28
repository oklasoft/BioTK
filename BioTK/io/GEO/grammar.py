# Experimentation on parsing SOFT with pyparsing

from pyparsing import *
import gzip

token = Word(alphas + "_")
comment = Suppress("#") + empty + restOfLine

header = Suppress(Literal("^Annotation")) + empty + restOfLine
date = Suppress(Literal("!Annotation_date")) + Suppress(Literal("= ")) + restOfLine
accession = Suppress(Literal("!Annotation_platform")) + Suppress(Literal("= ")) + restOfLine

parser = header + OneOrMore(date | accession)

with gzip.open("/home/gilesc/GPL96.annot.gz", "rt") as h:
    s = "".join(h.readlines()[:5])
    o = parser.parseString(s)
    print(o)
