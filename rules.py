
from collections import namedtuple

tags = {'offensive':'term which many trans people find offensive',
        'inaccurate':'inaccurate usage',
        'inappropriate':'Many trans and intersex people consider this terms inappropriate'}

RegRule = namedtuple('RegRule', ['rule','tag'])

regexRules = [RegRule(r'[pP]ost.[oO]p','offensive'),
              RegRule(r'[pP]re.[oO]p','offensive'),
              RegRule(r'[sS]ex.[cC]hange','offensive'),
              RegRule(r'[sS]ex.[sS]wap','offensive'),
              RegRule(r'[sS]he[mM]ale','offsensive'),
              RegRule(r'[hH]e[sS]he','offsensive'),
              RegRule(r'[gG]ender[bB]ender','offsensive'),
              RegRule(r'[hH]ermaphrodite','offsensive'),
              RegRule(r'[tT]ranssexuality','inaccurate'),
              RegRule(r'[tT]ransgendered','inaccurate'),
              RegRule(r'[gG]ender.[iI]dentity.[cC]onfusion','inaccurate'),
              RegRule(r'[gG]ender.[iI]dentity.[dD]isorder','inappropriate'),
              RegRule(r'[gG]ender.[dD]ysmorphia','inaccurate'),
              RegRule(r'[gG]ender.[rR]ealignment','inaccurate'),
              RegRule(r'[bB]orn a ([wW]o)?[mM]an','inaccurate'),
              RegRule(r'[sS]ex.[rR]eassignment.[sS]urgery','inappropriate'),
              RegRule(r'[gG]ender.[rR]eassignment.[sS]urgery','inappropriate')]


