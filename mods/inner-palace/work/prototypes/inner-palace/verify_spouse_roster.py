"""Replay the observed removed-spouse roster state against emitted UI filtering.

The native engine supplies the two lists. This fixture models the observed case:
Feng remains in the faction/family tree but is absent from NoblesCharacterList.
Live engine acceptance is tracked separately in the reference audit.
"""
from pathlib import Path
from types import SimpleNamespace as NS
import re, sys
import xml.etree.ElementTree as E

B = Path(__file__).resolve().parent
path = Path(sys.argv[1]) if len(sys.argv)>1 else B/'fixed_fourteen_src/ui/syc_harem_native/roster.twui.xml'
root=E.parse(path)
expr=next(c.get('context_function_id') for c in root.findall('.//callback_with_context')
          if c.get('callback_id')=='List' and 'Filter(' in c.get('context_function_id',''))
match=re.search(r'(\w+)\.Filter\(\(x\) => (.*)\)\)',expr)
assert match, expr
source,predicate=match.groups()
assert 'IsContextValid(x.SpouseContext)' in predicate, 'Global function arguments must name the lambda variable'

def woman(name, unmarried, spouse=False, **kw):
    return dict(Name=name, IsTemporaryCommander=False, IsBanished=False, IsAlive=True,
                ComeOfAge=True, IsMale=False, IsEligibleForMarriage=unmarried,
                SpouseContext=NS(IsFactionLeader=True,FactionContext=NS(IsPlayersFaction=True)) if spouse else None, **kw)
daughter=woman('Yuan daughter',True)
feng=woman('Feng',False,True)
other=woman('Other married woman',False)
dead=woman('Dead woman',True);dead['IsAlive']=False
banished=woman('Banished woman',True);banished['IsBanished']=True
minor=woman('Minor',True);minor['ComeOfAge']=False
male=woman('Man',True);male['IsMale']=True
lists={'NoblesCharacterList':[daughter], 'CharacterList':[daughter,feng,other,dead,banished,minor,male]}
condition=predicate.replace('&&',' and ').replace('||',' or ').replace('false','False').replace('true','True')
actual=[c['Name'] for c in lists[source] if eval(condition,{'__builtins__':{}},dict(x=NS(**c),IsContextValid=lambda c:c is not None))]
assert actual==['Yuan daughter','Feng'], f'removed spouse must remain selectable: {actual}'
count=next(c.get('context_function_id') for c in root.findall('.//callback_with_context') if '.Size)' in c.get('context_function_id','') and 'Filter(' in c.get('context_function_id',''))
assert f'{source}.Filter((x) => {predicate})' in count
print('PASS: removed spouse remains selectable; count matches; other married/dead/banished/minor/male excluded.')
