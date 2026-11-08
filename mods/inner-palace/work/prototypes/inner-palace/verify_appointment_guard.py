"""Evaluate the generated appointment predicate against eligibility cases.

This checks the emitted CCO boolean expression, not the engine's family data.
Engine property semantics and disabled-slot behavior still need live checks.
"""
from pathlib import Path
from types import SimpleNamespace as NS
import sys
import xml.etree.ElementTree as E

B = Path(__file__).resolve().parent
path = Path(sys.argv[1]) if len(sys.argv) > 1 else B/'independent_five_src/ui/syc_harem_native/minister_slot.twui.xml'
root = E.parse(path)
command = next(p.get('value') for p in root.findall('.//property') if p.get('name') == 'equip_command')
condition = command[len('DoIf('):command.index(', Do(')]
selection = 'Component("F49F83BC-0CEE-4BCE-8DE2EA61AB8D5B39").CurrentSelection.FirstObject'
expression = condition.replace(selection, 'selected').replace('&&', ' and ').replace('||', ' or ').replace('false', 'False').replace('true', 'True')

cases = [
    ('adult unmarried daughter', False, True, True, True, False, False),
    ('adult unmarried adopted relative', False, True, True, True, False, False),
    ('unrelated adult unmarried woman', False, True, True, False, False, True),
    ('current leader spouse', False, True, False, True, True, True),
    ('other married woman', False, True, False, False, False, False),
    ('minor', False, False, True, False, False, False),
    ('male', True, True, True, False, False, False),
]
for name, male, adult, unmarried, family, spouse, expected in cases:
    selected = NS(IsMale=male, ComeOfAge=adult, IsEligibleForMarriage=unmarried,
                  IsInFactionLeadersFamily=family,
                  SpouseContext=NS(IsFactionLeader=True, FactionContext=NS(IsPlayersFaction=True)) if spouse else None)
    actual = bool(eval(expression, {'__builtins__': {}}, {'selected': selected, 'IsContextValid': lambda c: c is not None}))
    assert actual == expected, f'{name}: expected {expected}, got {actual}'
    print('PASS', name)
