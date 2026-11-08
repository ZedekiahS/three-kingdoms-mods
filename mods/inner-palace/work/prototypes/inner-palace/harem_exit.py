"""Clone CA's divorce action and compose its native divorce/unassign payloads."""
from native_db import read, write, independent_header

ACTION='syc_harem_action_leave_marriage'
PAYLOAD='syc_harem_payload_leave_marriage'
MEMBER='syc_harem_member_leave_marriage'
NATIVE_ACTION='3k_main_campaign_group_political_action_divorce'
NATIVE_PAYLOAD='3k_main_campaign_payload_character_action_divorce'

def build_exit(put):
    replacements={NATIVE_ACTION:ACTION,NATIVE_PAYLOAD:PAYLOAD,
                  '3k_main_campaign_group_member_political_action_divorce':MEMBER}
    tables=['campaign_groups_tables','campaign_group_members_tables',
            'campaign_group_member_criteria_character_actions_tables',
            'campaign_group_character_actions_tables','ui_character_actions_tables',
            'campaign_payloads_tables','campaign_payload_basic_components_tables',
            'campaign_payload_effect_bundles_tables','campaign_payload_relationship_triggers_tables',
            'campaign_payload_resource_transactions_tables']
    result={}
    for table in tables:
        header,schema,base=read(table)
        rows=[]
        for row in base:
            if any(v in replacements for v in row.values() if isinstance(v,str)):
                clone={k:replacements.get(v,v) if isinstance(v,str) else v for k,v in row.items()}
                # Harem is a court page: let CA enumerate and execute this
                # action normally, without remapping a different UI action.
                if table=='ui_character_actions_tables':clone['category']='court'
                # This table has an integer primary key; allocate after native max.
                if table=='campaign_payload_relationship_triggers_tables':clone['id']=max(r['id'] for r in base)+1
                rows.append(clone)
        if table=='campaign_payload_basic_components_tables':
            rows.append(dict(component_type='unassign_from_post',payload=PAYLOAD))
        if table=='campaign_payload_effect_bundles_tables':
            rows.append(dict(duration=0,effect_bundle='3k_dummy_effect_bundle_character_action_unassign_from_post',payload=PAYLOAD))
        assert rows,table
        put('db/'+table+'/syc_harem_exit',write(independent_header(header,'harem_exit/'+table),schema,rows))
        result[table]=rows
    return result
