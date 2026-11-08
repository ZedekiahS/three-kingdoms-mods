"""Native court fork. Retain CA roster, cards, staged appointment and tooltips."""
from pathlib import Path
import copy, re, uuid, struct, json, sys
import xml.etree.ElementTree as E
from native_db import ROOT,read,write,independent_header
B=Path(__file__).resolve().parent
GLOBAL_REFERENCE='--all-factions-reference' in sys.argv
FIXED='--fixed-slots' in sys.argv
FIVE='--independent-five' in sys.argv or FIXED
REFERENCE='--liu-biao-reference' in sys.argv or GLOBAL_REFERENCE
MODE='fixed_fourteen' if FIXED else 'independent_five' if FIVE else 'global_reference' if GLOBAL_REFERENCE else 'reference_pilot' if REFERENCE else 'court_copy'
OUT=B/(MODE+'_src')
V=ROOT/'court_readout/vanilla/ui/campaign ui'
GUID=r'[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{16}'
def uid(s):
    h=uuid.uuid5(uuid.NAMESPACE_URL,'syc-native-court/'+s).hex.upper()
    return h[:8]+'-'+h[8:12]+'-'+h[12:16]+'-'+h[16:]
def remap(element,scope):
    text=E.tostring(element,encoding='unicode')
    for old in set(re.findall(GUID,text)):text=text.replace(old,uid(scope+old))
    return E.fromstring(text)
def put(path,data):
    p=OUT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
def xml(path,r):
    E.indent(r);put(path,E.tostring(r,encoding='utf-8',xml_declaration=True))
def comp(r,id):return next(c for c in r.find('components') if c.get('id')==id)
def callbacks(c):
    return c.findall('./callbackwithcontextlist/*')+c.findall('./callbacks_with_context/*')
def creator(c,path):
    cb=next(c for c in callbacks(c) if c.get('callback_id')=='ComponentCreator')
    cb.attrib.clear();cb.set('callback_id','ComponentCreator');cb[:]=[]
    E.SubElement(E.SubElement(cb,'child_m_user_properties'),'property',name='layout',value=path)

# Copy the original court content container, with independent content IDs.
# Its selection parent remains the existing native family_court_panel, so both
# pages use CA's CurrentSelection, character sidebar and CourtScreenStagedSlot.
court=E.parse(V/'family_court_panel.twui.xml').getroot()
hier=court.find('./hierarchy/root/family_court_panel');comps=court.find('components')
original_h=hier.find('court_screen')
clone=E.Element('clone');clone.append(copy.deepcopy(original_h))
owned={n.get('this') for n in original_h.iter()}
# Only center_panel, positions and lists are needed; governor deployment is not.
keep_h=clone[0];keep_h[:]=[keep_h.find('center_panel')]
owned={n.get('this') for n in keep_h.iter()}
for c in list(comps):
    if c.get('this') in owned:clone.append(copy.deepcopy(c))
text=E.tostring(clone,encoding='unicode')
owned_guids=set()
for c in clone[1:]:
    owned_guids.update(re.findall(GUID,E.tostring(c,encoding='unicode')))
# External parent GUID is deliberately shared, not remapped.
owned_guids.discard('F49F83BC-0CEE-4BCE-8DE2EA61AB8D5B39')
for old in owned_guids:text=text.replace(old,uid('page/'+old))
clone=E.fromstring(text);h=clone[0];h.tag='syc_harem_native_page'
pageid=h.get('this')
for c in clone[1:]:
    if c.get('id')=='court_screen':c.tag='syc_harem_native_page';c.set('id','syc_harem_native_page');c.set('visible','false')
    if c.get('id')=='center_panel':c.set('id','syc_harem_center');c.set('visible','true')
    if c.get('id')=='positions':creator(c,'ui/syc_harem_native/positions')
    if c.get('id')=='lists':creator(c,'ui/syc_harem_native/roster')
    comps.append(c)
hier.insert(list(hier).index(original_h)+1,h)
tab=remap(comp(court,'button_tab_court'),'tab/')
tab.tag='button_tab_syc_harem';tab.set('id','syc_harem_native_open')
for p in tab.findall('.//property'):
    if p.get('name')=='panel':p.set('value',pageid)
# Restore the shared selection parent reference after component remapping.
for cb in callbacks(tab):
    if cb.get('callback_id')=='ContextCommandLeftClick':
        cb.set('context_function_id','Component("F49F83BC-0CEE-4BCE-8DE2EA61AB8D5B39").ClearSelection')
for t in tab.findall('./localised_texts/*'):
    if t.get('state'):t.set('text','后宫');t.attrib.pop('text_label',None)
comps.append(tab);E.SubElement(hier.find('tab_buttons'),'button_tab_syc_harem',this=tab.get('this'))
xml('ui/campaign ui/family_court_panel.twui.xml',court)

# Use the native family-tree source, not the court's idle-noble subset: the
# latter omits some family-only spouses even after they leave an office.
roster=E.parse(V/'court_screen_info_lists.twui.xml').getroot()
spouse_eligible='(IsContextValid(x.SpouseContext) && x.SpouseContext.IsFactionLeader && x.SpouseContext.FactionContext.IsPlayersFaction)'
predicate='x.IsTemporaryCommander == false && x.IsBanished == false && x.IsAlive && x.ComeOfAge && x.IsMale == false && (x.IsEligibleForMarriage || '+spouse_eligible+')'
changed=0
for cb in roster.findall('.//callback_with_context'):
    expr=cb.get('context_function_id','')
    if 'Filter(NoblesCharacterList' in expr:
        cb.set('context_function_id',expr.replace('Filter(NoblesCharacterList, {IsTemporaryCommander == false && ComeOfAge})','CharacterList.Filter((x) => '+predicate+')'));changed+=1
assert changed==2
# Unhired candidates are not faction members and cannot be appointed.
comp(roster,'candidates').set('visible','false')
comp(roster,'candidates').set('id','syc_hidden_recruitment')
for cb in callbacks(comp(roster,'syc_hidden_recruitment')):
    if cb.get('callback_id')=='ContextVisibilitySetter':cb.set('context_function_id','false')
xml('ui/syc_harem_native/roster.twui.xml',roster)

# Keep the entire original minister card/staging template. Only guard eligibility
# in its existing equip command. The native callback supplies preview and commit.
slot=E.parse(V/'court_screen_minister_slot.twui.xml').getroot()
selected='Component("F49F83BC-0CEE-4BCE-8DE2EA61AB8D5B39").CurrentSelection.FirstObject'
spouse_guard='(IsContextValid('+selected+'.SpouseContext) && '+selected+'.SpouseContext.IsFactionLeader && '+selected+'.SpouseContext.FactionContext.IsPlayersFaction)'
# Native dialog_action_confirmation uses IsInFactionLeadersFamily for family
# membership. Keep relatives in the roster, but allow only the leader's spouse
# as a family exception at the actual appointment boundary.
appointment_guard=selected+'.IsMale == false && '+selected+'.ComeOfAge && (('+selected+'.IsEligibleForMarriage && '+selected+'.IsInFactionLeadersFamily == false) || '+spouse_guard+')'
blocked_selection='IsContextValid('+selected+') && ('+appointment_guard+') == false'
for p in slot.findall('.//property'):
    if p.get('name')=='equip_command':
        old=p.get('value');p.set('value','DoIf('+appointment_guard+', '+old+')')
    if p.get('name')=='state_expression' and '.PostAssignmentState(this)' in p.get('value',''):
        p.set('value','GetIfElse('+blocked_selection+', "inactive", '+p.get('value')+')')
for cb in callbacks(comp(slot,'character_slot_staged')):
    if cb.get('callback_id')=='ContextTooltipSetter':
        cb.set('context_function_id','GetIfElse('+blocked_selection+', "不能册封：仅限非君主家族的成年未婚女性，或君主现任配偶。家族成员可以在右侧查看。", Component("F49F83BC-0CEE-4BCE-8DE2EA61AB8D5B39").PostTooltip(this))')
xml('ui/syc_harem_native/minister_slot.twui.xml',slot)
if FIXED:
    # Reuse the native card unchanged; hide repeated headers, and center the
    # first noble's header between its two cards using native docking offsets.
    for variant in ['no_header','noble_header']:
        variant_slot=copy.deepcopy(slot)
        for header_id in ['minister_header','minister_header_faction_council_post']:
            header=comp(variant_slot,header_id)
            if variant=='no_header':
                header.set('visible','false')
                for cb in callbacks(header):
                    if cb.get('callback_id')=='ContextVisibilitySetter':cb.set('context_function_id','false')
            else:
                x,y=map(float,header.get('dock_offset').split(','))
                header.set('dock_offset',f'{x+85:.2f},{y:.2f}')
        xml('ui/syc_harem_native/minister_slot_'+variant+'.twui.xml',variant_slot)

# Copy the native top row / five-slot row. Change only post keys and arrangement.
layout=E.parse(V/'court_screen.twui.xml').getroot()
lc=layout.find('components');lh=layout.find('./hierarchy/root/court_screen/positions')
slot_base=copy.deepcopy(comp(layout,'3k_main_court_offices_prime_minister'))
leader=copy.deepcopy(comp(layout,'faction_leader'))
pos=comp(layout,'positions')
print('native positions',pos.attrib)
old_ids={n.get('this') for n in lh.iter() if n is not lh}
for c in list(lc):
    if c.get('this') in old_ids:lc.remove(c)
lh[:]=[]
# Use original layout coordinates rather than Lua screen-space scaling.
if pos.find('LayoutEngine') is not None:pos.remove(pos.find('LayoutEngine'))
for key in ['docking','component_anchor_point','dock_offset']:pos.attrib.pop(key,None)
pos.set('offset','0.00,0.00')
for state in pos.findall('./states/*'):state.set('width','1920');state.set('height','1080')
leader.set('offset','800.00,140.00')
for k in ['docking','component_anchor_point','dock_offset']:leader.attrib.pop(k,None)
lc.append(leader);E.SubElement(lh,'faction_leader',this=leader.get('this'))
groups=[('queen','皇后',1,[(1030,165)]),('noble','贵人',2,[(440,440),(610,440)]),('beauty','美人',3,[(950,440),(1120,440),(1290,440)]),('attendant','宫人',3,[(300,735),(450,735),(600,735)]),('chosen','采女',5,[(850,735),(1000,735),(1150,735),(1300,735),(1450,735)])]
reference_keys=['3k_main_court_offices_liu_biao_academy_tutor','3k_main_court_offices_liu_biao_academy_scholar','3k_main_court_offices_liu_biao_academy_student']
if REFERENCE:
    # One native post group per rank; CA's CharacterList renders its occupants.
    groups=[('queen','皇后',1,[(1030,165)]),('noble','贵人',2,[(500,470)]),('beauty','美人',3,[(1080,470)])]
if FIVE and not FIXED:
    groups=[('queen','皇后',1,[(1030,165)]),('noble','贵人',2,[(430,440)]),('beauty','美人',3,[(1030,440)]),('attendant','宫人',3,[(430,735)]),('chosen','采女',5,[(1030,735)])]
posts=[]
for rank,(kind,name,count,coords) in enumerate(groups):
    for i,(x,y) in enumerate(coords,1):
        key=reference_keys[rank] if REFERENCE else 'syc_harem_'+kind+'_'+str(i)
        posts.append((key,name,rank))
        tag='_'+key if key[0].isdigit() else key
        c=remap(slot_base,key);c.tag=tag;c.set('id',key);c.set('offset',f'{x:.2f},{y:.2f}')
        for k in ['docking','component_anchor_point','dock_offset']:c.attrib.pop(k,None)
        template='ui/syc_harem_native/minister_slot'
        if FIXED and count>1:
            if count==2 and i==1:template+='_noble_header'
            elif i!=(count+1)//2:template+='_no_header'
        creator(c,template)
        for p in c.findall('.//property'):
            if p.get('name')=='target':p.set('value','court_screen_minister_slot')
        lc.append(c);E.SubElement(lh,tag,this=c.get('this'))
# The palace picture is copied from CA's imperial court and appears only when
# the native layout resolver selects that exact court; non-emperor stays native.
imperial=E.parse(V/'court_screen_imperial_court.twui.xml').getroot()
art=copy.deepcopy(comp(imperial,'court_screen_imperial_court'))
if art.find('componentimages') is not None:
    ar=remap(art,'palace');ar.tag='syc_palace';ar.set('id','syc_palace')
    cb=ar.find('callbackwithcontextlist')
    if cb is None:cb=E.SubElement(ar,'callbackwithcontextlist')
    E.SubElement(cb,'callback_with_context',callback_id='ContextVisibilitySetter',context_object_id='CcoStaticObject',context_function_id='Component("F49F83BC-0CEE-4BCE-8DE2EA61AB8D5B39").GetLayoutString("court_screen") == "ui/campaign ui/court_screen_imperial_court"')
    lc.append(ar);layout.find('./hierarchy/root/court_screen').insert(0,E.Element('syc_palace',this=ar.get('this')))
xml('ui/syc_harem_native/positions.twui.xml',layout)

# The same native sidebar serves court, family tree and harem. Only the harem
# branch changes its actions; confirmation, validity and payload execution stay
# native. Native AvailableActionsList's first argument selects family actions.
from harem_actions import patch_actions
patch_actions(court,pageid,[key for key,_,_ in posts])
xml('ui/campaign ui/family_court_panel.twui.xml',court)

# New native posts, independent keys; never rename/replace existing court posts.
tables={t:read(t) for t in ['ministerial_positions_tables','ministerial_positions_culture_details_tables','ministerial_positions_to_government_types_tables','ministerial_positions_to_effects_tables','ministerial_positions_to_character_effects_tables','ui_ministerial_positions_tables']}
new={t:[] for t in tables}
base=next(r for r in tables['ministerial_positions_tables'][2] if r['minister_key']=='3k_main_court_offices_prime_minister')
culture=next(r for r in tables['ministerial_positions_culture_details_tables'][2] if r['ministerial_position_cultural_variant']=='3k_main_court_offices_minister_prime_minister')
effects=tables['ministerial_positions_to_effects_tables'][2]
loc=[]
for key,name,rank in posts:
    row=dict(base,minister_key=key,power_rating=[10,8,4,2,1][rank],minimum_term_length=0)
    if FIVE:row.update(maximum_concurrent_ministers=1 if FIXED else [1,2,3,3,5][rank],minimum_age=18,maximum_age=999,must_have_come_of_age=True)
    if REFERENCE:
        row=dict(next(r for r in tables['ministerial_positions_tables'][2] if r['minister_key']==key),minimum_age=18,maximum_age=999,must_have_come_of_age=True,maximum_concurrent_ministers=[1,2,3][rank],minimum_term_length=0,power_rating=[10,8,4][rank])
    new['ministerial_positions_tables'].append(row)
    source_culture=next(r for r in tables['ministerial_positions_culture_details_tables'][2] if r['ministerial_position_key']==key and r['faction_key']=='3k_main_faction_liu_biao') if REFERENCE else culture
    variant=source_culture['ministerial_position_cultural_variant'] if REFERENCE else key
    label=('syc_reference_'+groups[rank][0]) if REFERENCE else key
    row=dict(source_culture,localised_string_key=label,ministerial_position_key=key,localised_description_key=label+'_description',ministerial_position_cultural_variant=variant,ui_record=source_culture['ui_record'] if REFERENCE else key,allow_character_to_factionwide_ministerial_effects=rank<2,allow_character_to_factionwide_ministerial_alternative_effects=False,faction_progression_level_requirement=0,character_rank_requirement=1)
    if GLOBAL_REFERENCE:row['faction_key']=None
    new['ministerial_positions_culture_details_tables'].append(row)
    if not REFERENCE:new['ui_ministerial_positions_tables'].append({'key':key,'backplate_image_path':None})
    for gov in ['gov_absolute_monarchy','gov_empire']:
        if not REFERENCE:new['ministerial_positions_to_government_types_tables'].append({'government_type':gov,'ministerial_position':key})
    choices=[('3k_main_effect_province_public_order_from_characters',2),('3k_main_effect_province_corruption',-1),('3k_main_effect_economy_gdp_mod_peasantry',2),('3k_main_effect_economy_gdp_mod_industry',1),('3k_main_effect_economy_gdp_mod_commerce',1)]
    effect,val=choices[rank]
    if REFERENCE:
        # Preserve row identities and neutralize the academy's experience bonus.
        # Other native records remain intact; the intended palace effects follow.
        for table in ['ministerial_positions_to_effects_tables','ministerial_positions_to_character_effects_tables']:
            for old in tables[table][2]:
                if old['ministerial_position_cultural_variant']==variant and old['effect']=='3k_main_effect_characters_experience_bonus':
                    new[table].append(dict(old,value=0))
    src=next(r for r in effects if r['effect']==effect)
    new['ministerial_positions_to_effects_tables'].append(dict(src,value=val,minister_level=1,ui_id=1,ministerial_position_cultural_variant=variant))
    # Native rank/salary/satisfaction handling, without invented faction bonuses.
    new['ministerial_positions_to_character_effects_tables'].append(dict(effect='3k_main_dummy_effect_ministerial_position_power_rank',effect_scope='character_to_character_own',minister_level=1,ui_id=0,value=[10,8,4,2,1][rank],ministerial_position_cultural_variant=variant,ceo_node=None))
    desc=['统理六宫，协和内外。','协理内廷，整肃家政。','劝农养民，丰衣足食。','掌理营造，节用裕民。','通商理财，四方流通。'][rank]
    if FIVE:desc+=('本位一人，本组共' if FIXED else '名额上限：')+str([1,2,3,3,5][rank])+'人。'
    desc+='限非君主家族的成年未婚女性，或本派系君主的成年女性配偶。'+('任职时启用该人物的派系范围增益。' if rank<2 else '此名位不启用该人物的派系范围增益。')
    loc.extend([('ministerial_positions_strings_on_screen_'+label,name,False),('ministerial_positions_strings_on_screen_'+label+'_description',desc,False)])
for table,(header,schema,_) in tables.items():
    if new[table]:put('db/'+table+'/syc_harem_native',write(independent_header(header,('reference/' if REFERENCE else 'independent/')+table),schema,new[table]))
def u16(s):
    b=s.encode('utf-16le');return struct.pack('<H',len(b)//2)+b
from harem_exit import build_exit, ACTION
build_exit(put)
loc.extend([
    ('ui_character_actions_localised_title_'+ACTION, '休妻（移出后宫）', False),
    ('ui_character_actions_localised_fallback_tooltip_'+ACTION, '解除与君主的婚姻，同时移除后宫名位。改封请直接选择其他名位，保留婚姻。', False),
])
locbytes=b'\xff\xfeLOC\0'+struct.pack('<II',1,len(loc))+b''.join(u16(k)+u16(v)+bytes([tip]) for k,v,tip in loc)
from read_mods import parse_loc
assert parse_loc(locbytes)==[list(r) for r in loc]
put('text/syc_harem_native.loc',locbytes)
# Disable the old prototype initializer in a predictable way when replacing pack.
diagnostic=(B/'native_court_diagnostic.lua').read_text(encoding='utf-8')
if FIVE:
    diagnostic=(B/'spouse_queen.lua').read_text(encoding='utf-8')+'\n'+diagnostic
    diagnostic=diagnostic.replace('cm:add_first_tick_callback(inspect)', '''cm:add_first_tick_callback(function() syc_initialise_spouse_queen();inspect() end)
 for _,event in ipairs({'CharacterMarried','CharacterBecomesFactionLeader'}) do
  core:add_listener('syc_spouse_'..event,event,true,function()
   cm:callback(syc_initialise_spouse_queen,0.2)
  end,true)
 end''')
if REFERENCE:diagnostic=diagnostic.replace('syc_harem_queen_1',reference_keys[0]).replace('[SYC NATIVE CHECK]','[SYC REFERENCE CHECK]')
put('script/campaign/mod/syc_harem_preview.lua',diagnostic.encode('utf-8'))
files=sorted(p for p in OUT.rglob('*') if p.is_file());index=b'';body=b''
for p in files:
    data=p.read_bytes();index+=struct.pack('<IB',len(data),0)+str(p.relative_to(OUT)).replace('/','\\').encode()+b'\0';body+=data
pack=B/('zz_syc_harem_fixed_fourteen.pack' if FIXED else 'zz_syc_harem_independent_five.pack' if FIVE else 'zz_syc_harem_global_reference.pack' if GLOBAL_REFERENCE else 'zz_syc_harem_reference_pilot.pack' if REFERENCE else 'zz_syc_harem_native_court.pack')
pack.write_bytes(struct.pack('<4s6I',b'PFH5',4,0,0,len(files),len(index),0)+index+body)
(B/(MODE+'_manifest.json')).write_text(json.dumps({'status':'built; runtime verification pending','mode':MODE,'posts':posts,'files':[str(p.relative_to(OUT)) for p in files]},ensure_ascii=False,indent=2),encoding='utf-8')
print(pack,len(files),pack.stat().st_size)
