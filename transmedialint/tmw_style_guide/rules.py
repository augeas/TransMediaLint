
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

regexRules = [(r'post.op', offensive, 'post-op'),
              (r'pre.op', offensive, 'pre-op'),
              (r'sex.change', offensive, 'sex-change'),
              (r'sex.swap', offensive, 'sex-swap'),
              (r'shemale', offensive, 'shemale'),
              (r'heshe',offensive, 'heshe'),
              (r'gender.?bender',offensive, 'gender bender'),
              (r'hermaphrodite', offensive, 'hermaphrodite'),
              (r'tranny', offensive, 'tranny'),
              (r'transsexuality', inaccurate, 'transsexuality'),
              (r'transgendered', inaccurate, 'transgendered'),
              (r'transgenderism', inaccurate, 'transgenderism'),
              (r'gender.identity.confusion', inaccurate,'gender identity confusion'),
              (r'gender.identity.disorder', inappropriate_medical,'gender identity disorder'),
              (r'disorders?.of.sexual.development', inappropriate_medical,'disorders of sexual development'),
              (r'gender.dysmorphia', inaccurate, 'gender dysmorphia'),
              (r'gender.realignment', inaccurate, 'gender realignment'),
              (r'born a (?:wo)?man', inaccurate, 'born a (wom)an'),
              (r'bec[ao]me a (?:wo)?man', inaccurate, 'become a (wo)man'),
              (r'sex.reassignment.surgery', inappropriate_medical,'sex reassignment surgery'),
              (r'gender.reassignment.surgery', inappropriate_medical,'gender reassignment surgery'),
              (r'"(?:boy|girl|man|woman|he|she)"', offensive, 'scare-quotes')]
              
rules = [RegRule(re.compile(rule, flags=re.IGNORECASE),tag,label) for rule,tag,label in regexRules]

