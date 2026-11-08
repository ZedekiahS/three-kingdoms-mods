"""Reuse CA action enumeration, confirmation, validity and execution unchanged."""
from harem_exit import ACTION

def patch_actions(court, pageid, postkeys):
    visible=f'Component("{pageid}").IsVisible'
    character='Component("BB52800B-3C9A-4DB8-B3346DDBDDEAC443").StoredContext("CcoCampaignCharacter")'
    spouse=f'(IsContextValid({character}.SpouseContext) && {character}.SpouseContext.IsFactionLeader && {character}.SpouseContext.FactionContext.IsPlayersFaction)'
    unassign='"3k_main_campaign_group_political_action_unassign_from_post"'
    for c in court.find('components'):
        for cb in c.findall('.//callback_with_context'):
            expr=cb.get('context_function_id','')
            if c.get('id') in ('template_action','template_action_with_target') and cb.get('callback_id') is None and 'UiRecordContext.RequiresTarget' in expr:
                show=f'(({visible} == false && UiRecordContext.Key != "{ACTION}") || ({visible} && ((UiRecordContext.Key == "{ACTION}" && {spouse}) || (UiRecordContext.Key == {unassign} && {spouse} == false))))'
                cb.set('context_function_id',f'({expr}) && {show}')
            if cb.get('callback_id')=='ContextTextLabel' and expr=='ToUpper(UiRecordContext.LocalisedTitle)':
                cb.set('context_function_id',f'GetIfElse({visible} && UiRecordContext.Key == {unassign}, "移出后宫", {expr})')
