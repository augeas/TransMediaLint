
from collections import namedtuple
import re

tags = {'offensive':'term which many trans people find offensive'}

RegRule = namedtuple('RegRule', ['rule','tag'])

regexRules = [RegRule(r'[pP]ost.[oO]p','offensive'),
              RegRule(r'[pP]re.[oO]p','offensive'),
              RegRule(r'[sS]ex.[cC]hange','offensive'),
              RegRule(r'[sS]ex.[sS]wap','offensive')]

