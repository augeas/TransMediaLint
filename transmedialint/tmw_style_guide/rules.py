
from collections import namedtuple

offensive = 'offensive'
inaccurate = 'inaccurate'
inappropriate = 'inappropriate'
inappropriate_medical = 'inappropriate-medical'


tags = {offensive:'term which many trans people find offensive',
        inaccurate:'inaccurate usage',
        inappropriate:'Many trans and intersex people consider this term inappropriate'}

RegRule = namedtuple('RegRule', ['rule', 'tag', 'label'])

regexRules = [RegRule(r'[pP]ost.[oO]p', offensive, 'post-op'),
              RegRule(r'[pP]re.[oO]p', offensive, 'pre-op'),
              RegRule(r'[sS]ex.[cC]hange', offensive, 'sex-change'),
              RegRule(r'[sS]ex.[sS]wap', offensive, 'sex-swap'),
              RegRule(r'[sS]he[mM]ale', offensive, 'shemale'),
              RegRule(r'[hH]e[sS]he',offensive, 'heshe'),
              RegRule(r'[gG]ender\s?[bB]ender',offensive, 'gender bender'),
              RegRule(r'[hH]ermaphrodite', offensive, 'hermaphrodite'),
              RegRule(r'[tT]ranny', offensive, 'tranny'),
              RegRule(r'[tT]ranssexuality', inaccurate, 'transsexuality'),
              RegRule(r'[tT]ransgendered', inaccurate, 'transgendered'),
              RegRule(r'[gG]ender.[iI]dentity.[cC]onfusion', inaccurate,
                'gender identity confusion'),
              RegRule(r'[gG]ender.[iI]dentity.[dD]isorder', inappropriate_medical,
                'gender identity disorder'),
              RegRule(r'[dD]isorders?.of.[sS]exual.[dD]evelopment', inappropriate_medical,
                'disorders of sexual development'),
              RegRule(r'[gG]ender.[dD]ysmorphia', inaccurate, 'gender dysmorphia'),
              RegRule(r'[gG]ender.[rR]ealignment', inaccurate, 'gender realignment'),
              RegRule(r'[bB]orn a ([wW]o)?[mM]an', inaccurate, 'born a (wom)an'),
              RegRule(r'[bB]ec[ao]me a ([wW]o)?[mM]an', inaccurate, 'become a (wo)man'),
              RegRule(r'[sS]ex.[rR]eassignment.[sS]urgery', inappropriate_medical,
                'sex reassignment surgery'),
              RegRule(r'[gG]ender.[rR]eassignment.[sS]urgery', inappropriate_medical,
                'gender reassignment surgery'),
              RegRule(r'(\"[mM]an\")|(\"[wW]oman\")|(\"[mM]ale\")|(\"[fF]emale\")|(\"[bB]oy\")|(\"[gG]irl\")|(\"[hH]e\")|(\"[sS]he\")', offensive, 'scare-quotes')]

