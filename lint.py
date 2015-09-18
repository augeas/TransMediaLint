from collections import namedtuple
from itertools import chain
import re
from rules import regexRules

Annotation2 = namedtuple('Annotation', ['start','end','tag'])

def getAnnotations(rule,doc):
    return [Annotation2(*[i for i in chain(match.span(),(rule.tag,))]) for match in re.finditer(rule.rule,doc)]

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


Annotation = namedtuple('Annotation', ['what', 'where', 'why'])

def annotate(text):

    issues_list = []

    for rule in regexRules:
        for match in re.finditer(rule.rule, text):

            issues_list.append(
                Annotation(match.group(), match.span()[0], rule.tag)
            )

    return issues_list

def score(text):

    annotation_points = {
        'inappropriate': -1,
        'inaccurate': -2,
        'offensive': -5
    }

    annotations = annotate(text)

    return sum(
        annotation_points[annotation.why]

        for annotation in annotations
    )
