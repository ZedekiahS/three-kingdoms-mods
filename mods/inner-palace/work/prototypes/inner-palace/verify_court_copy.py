from pathlib import Path
import xml.etree.ElementTree as E
import json,sys,struct
from collections import Counter
from native_db import ROOT,read
from extract_traits import index_pack,read_entry
from read_mods import parse_loc
B=Path(__file__).resolve().parent;GLOBAL_REFERENCE='--all-factions-reference' in sys.argv
FIXED='--fixed-slots' in sys.argv
FIVE='--independent-five' in sys.argv or FIXED
REFERENCE='--liu-biao-reference' in sys.argv or GLOBAL_REFERENCE
MODE='fixed_fourteen' if FIXED else 'independent_five' if FIVE else 'global_reference' if GLOBAL_REFERENCE else 'reference_pilot' if REFERENCE else 'court_copy'
O=B/(MODE+'_src');V=ROOT/'court_readout/vanilla/ui/campaign ui'
def canonical(e):
    e=E.fromstring(E.tostring(e))
    for n in e.iter():n.text=(n.text or '').strip() or None;n.tail=None
    return E.tostring(e)
orig=E.parse(V/'family_court_panel.twui.xml');new=E.parse(O/'ui/campaign ui/family_court_panel.twui.xml')
newc={c.get('this'):c for c in new.find('components')}
action_changes=0
for c in orig.find('components'):
    updated=E.fromstring(E.tostring(newc[c.get('this')]))
    for a,b in zip(updated.findall('.//callback_with_context'),c.findall('.//callback_with_context')):
        expr=b.get('context_function_id','')
        patched=a.get('context_function_id','')
        if patched != expr:
            assert c.get('id') in ('template_action','template_action_with_target','action_label','action_label_with_target') or (b.get('callback_id')=='ContextTextLabel' and expr=='ToUpper(UiRecordContext.LocalisedTitle)'), c.get('id')
            assert b.get('callback_id') in (None,'ContextTextLabel'), 'Execution/validity/tooltip must stay native'
            if c.get('id')=='actions_list':raise AssertionError('Native action list must remain byte-for-byte unchanged')
            a.set('context_function_id',expr);action_changes+=1
    assert canonical(c)==canonical(updated),c.get('id')
assert action_changes==4, action_changes
# Native selection / preview / confirmation remains CA's implementation.
slot=E.parse(O/'ui/syc_harem_native/minister_slot.twui.xml')
base=E.parse(V/'court_screen_minister_slot.twui.xml')
changes=0
for a,b in zip(slot.getroot().iter(),base.getroot().iter()):
    if a.tag=='property' and a.get('name')=='equip_command':
        assert 'IsMale == false' in a.get('value') and 'IsEligibleForMarriage' in a.get('value')
        assert '.SpouseContext.IsFactionLeader' in a.get('value') and '.SpouseContext.FactionContext.IsPlayersFaction' in a.get('value')
        assert '.IsInFactionLeadersFamily == false' in a.get('value')
        a.set('value',b.get('value'));changes+=1
    elif a.tag=='property' and a.get('name')=='state_expression' and '.PostAssignmentState(this)' in a.get('value',''):
        assert '.IsInFactionLeadersFamily == false' in a.get('value') and '"inactive"' in a.get('value')
        a.set('value',b.get('value'));changes+=1
    elif a.get('callback_id')=='ContextTooltipSetter' and a.get('context_function_id','').startswith('GetIfElse(IsContextValid(Component('):
        assert '不能册封' in a.get('context_function_id')
        a.set('context_function_id',b.get('context_function_id'));changes+=1
assert changes==3 and canonical(slot.getroot())==canonical(base.getroot())
roster=E.parse(O/'ui/syc_harem_native/roster.twui.xml')
filters=[c.get('context_function_id') for c in roster.findall('.//callback_with_context') if 'CharacterList.Filter(' in c.get('context_function_id','')]
assert len(filters)==2 and all('IsMale == false' in x and 'IsEligibleForMarriage' in x and 'ComeOfAge' in x for x in filters)
assert all('IsContextValid(x.SpouseContext)' in x and 'SpouseContext.IsFactionLeader' in x and 'SpouseContext.FactionContext.IsPlayersFaction' in x for x in filters)
manifest=json.loads((B/(MODE+'_manifest.json')).read_text(encoding='utf-8'))
posts=manifest['posts'];assert [sum(r==i for _,_,r in posts) for i in range(5)]==([1,2,3,3,5] if FIXED else [1,1,1,1,1] if FIVE else [1,1,1,0,0] if REFERENCE else [1,2,3,3,5])
if FIXED:
    positions=E.parse(O/'ui/syc_harem_native/positions.twui.xml')
    components={c.get('id'):c for c in positions.find('components')}
    headers=Counter()
    for key,_,rank in posts:
        c=components[key]
        template=next(p.get('value') for p in c.findall('.//property') if p.get('name')=='layout')
        if not template.endswith('_no_header'):headers[rank]+=1
    assert [headers[i] for i in range(5)]==[1]*5
    for variant in ['no_header','noble_header']:
        modified=E.parse(O/('ui/syc_harem_native/minister_slot_'+variant+'.twui.xml'))
        reference=E.parse(O/'ui/syc_harem_native/minister_slot.twui.xml')
        for a,b in zip(modified.findall('./components/*'),reference.findall('./components/*')):
            if a.get('id') in ['minister_header','minister_header_faction_council_post']:
                if variant=='no_header':
                    assert a.get('visible')=='false'
                    assert all(n.get('context_function_id')=='false' for n in a.findall('.//callback_with_context') if n.get('callback_id')=='ContextVisibilitySetter')
                else:assert float(a.get('dock_offset').split(',')[0])-float(b.get('dock_offset').split(',')[0])==85
                a.attrib.clear();a.attrib.update(b.attrib);a[:]=list(b)
        assert canonical(modified.getroot())==canonical(reference.getroot())
for p in O.rglob('*.xml'):
    r=E.parse(p);ids=[c.get('this') for c in r.find('components')]
    assert len(ids)==len(set(ids)),p
    assert all(n.get('this') in ids for n in r.findall('.//hierarchy//*[@this]')),p
pack=B/('zz_syc_harem_fixed_fourteen.pack' if FIXED else 'zz_syc_harem_independent_five.pack' if FIVE else 'zz_syc_harem_global_reference.pack' if GLOBAL_REFERENCE else 'zz_syc_harem_reference_pilot.pack' if REFERENCE else 'zz_syc_harem_native_court.pack')
ix=index_pack(pack)
assert len(ix)==len(manifest['files'])
for e in ix:assert read_entry(pack,e)==(O/e['path']).read_bytes()
guids=[]
for e in ix:
    if not e['path'].startswith('db/'):continue
    data=read_entry(pack,e);header,_,_=read(e['path'].split('/')[1])
    n=struct.unpack_from('<H',data,4)[0];guid=data[6:6+n*2]
    assert guid!=header[6:6+struct.unpack_from('<H',header,4)[0]*2],e['path']
    guids.append(guid)
assert len(guids)==len(set(guids))
if REFERENCE:
    # The culture table's primary key is cultural_variant, not position/faction.
    # A reference adaptation must override the existing record, not add a rival.
    culture_bytes=(O/'db/ministerial_positions_culture_details_tables/syc_harem_native').read_bytes()
    if GLOBAL_REFERENCE:assert b'3k_main_faction_liu_biao' not in culture_bytes
    for key,_,_ in posts:
        original=next(r for r in read('ministerial_positions_culture_details_tables')[2] if r['ministerial_position_key']==key)
        encoded=original['ministerial_position_cultural_variant'].encode()
        assert culture_bytes.count(struct.pack('<H',len(encoded))+encoded)>=2, 'Native culture primary key was replaced: '+key
loc=parse_loc((O/'text/syc_harem_native.loc').read_bytes());assert len(loc)==2+(28 if FIXED else 10 if FIVE else 6 if REFERENCE else 28)
assert set(v for _,v,_ in loc if len(v)==2)>=({'皇后','贵人','美人'} if REFERENCE else {'皇后','贵人','美人','宫人','采女'})
assert b'fixed sample' not in (O/'script/campaign/mod/syc_harem_preview.lua').read_bytes()
print('PASS: original court UI/commands preserved outside harem-scoped action labels/list; native staged card identical except eligibility guard; full roster filters/count; post keys; XML links; pack readback; Chinese labels. Runtime verification is separate.')
