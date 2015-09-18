from collections import namedtuple
from itertools import chain
import re
from rules import regexRules

Annotation = namedtuple('Annotation', ['start','end','tag'])

def getAnnotations(rule,doc):
    return [Annotation(*[i for i in chain(match.span(),(rule.tag,))]) for match in re.finditer(rule.rule,doc)]

def annotatedDoc(doc,annotations):
    pointer = 0
    for anot in annotations:
        yield doc[pointer:anot.start]
        yield '<span class="'+anot.tag+'">'
        pointer = anot.end + 1
        yield doc[anot.start:pointer]
        yield '</span>'
    yield doc[pointer:]

def lintify(doc):
    annotations = sorted(chain(*[getAnnotations(rule,doc) for rule in regexRules]),key=lambda x: x.start)
    newDoc = ''.join([chunk for chunk in annotatedDoc(doc,annotations)])

    #print newDoc

    return len(annotations), annotations, newDoc


def annotate(text):
    pass





