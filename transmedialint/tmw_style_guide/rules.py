
from collections import namedtuple
import re

offensive = 'offensive'
inaccurate = 'inaccurate'
inappropriate = 'inappropriate'
inappropriate_medical = 'inappropriate_medical'

rule_tags = [offensive, inaccurate, inaccurate, inappropriate_medical]

tag_details = {offensive:'term which many trans people find offensive',
        inaccurate:'inaccurate usage',
        inappropriate:'many trans and intersex people consider this term inappropriate',
        inappropriate_medical:'medical/legal term that many trans and intersex people consider inappropriate'}

RegRule = namedtuple('RegRule', ['rule', 'tag', 'label'])

regexRules = [(r'[pP]ost.[oO]p', offensive, 'post-op'),
              (r'[pP]re.[oO]p', offensive, 'pre-op'),
              (r'[sS]ex.[cC]hange', offensive, 'sex-change'),
              (r'[sS]ex.[sS]wap', offensive, 'sex-swap'),
              (r'[sS]he[mM]ale', offensive, 'shemale'),
              (r'[hH]e[sS]he',offensive, 'heshe'),
              (r'[gG]ender\s?[bB]ender',offensive, 'gender bender'),
              (r'[hH]ermaphrodite', offensive, 'hermaphrodite'),
              (r'[tT]ranny', offensive, 'tranny'),
              (r'[tT]ranssexuality', inaccurate, 'transsexuality'),
              (r'[tT]ransgendered', inaccurate, 'transgendered'),
              (r'[tT]ransgenderism', inaccurate, 'transgenderism'),
              (r'[gG]ender.[iI]dentity.[cC]onfusion', inaccurate,'gender identity confusion'),
              (r'[gG]ender.[iI]dentity.[dD]isorder', inappropriate_medical,'gender identity disorder'),
              (r'[dD]isorders?.of.[sS]exual.[dD]evelopment', inappropriate_medical,'disorders of sexual development'),
              (r'[gG]ender.[dD]ysmorphia', inaccurate, 'gender dysmorphia'),
              (r'[gG]ender.[rR]ealignment', inaccurate, 'gender realignment'),
              (r'[bB]orn a ([wW]o)?[mM]an', inaccurate, 'born a (wom)an'),
              (r'[bB]ec[ao]me a ([wW]o)?[mM]an', inaccurate, 'become a (wo)man'),
              (r'[sS]ex.[rR]eassignment.[sS]urgery', inappropriate_medical,'sex reassignment surgery'),
              (r'[gG]ender.[rR]eassignment.[sS]urgery', inappropriate_medical,'gender reassignment surgery'),
              (r'(\"[mM]an\")|(\"[wW]oman\")|(\"[mM]ale\")|(\"[fF]emale\")|(\"[bB]oy\")|(\"[gG]irl\")|(\"[hH]e\")|(\"[sS]he\")',
               offensive, 'scare-quotes')]
              
rules = [RegRule(re.compile(rule),tag,label) for rule,tag,label in regexRules]

