"""Keep CA's action list; adapt the existing unassign button only in harem."""
from harem_exit import ACTION

def patch_actions(court, pageid, postkeys):
    visible=f'Component("{pageid}").IsVisible'
    panel='Component("F49F83BC-0CEE-4BCE-8DE2EA61AB8D5B39")'
    character='Component("BB52800B-3C9A-4DB8-B3346DDBDDEAC443").StoredContext("CcoCampaignCharacter")'
    unassign='"3k_main_campaign_group_political_action_unassign_from_post"'
    spouse=f'(IsContextValid({character}.SpouseContext) && {character}.SpouseContext.IsFactionLeader && {character}.SpouseContext.FactionContext.IsPlayersFaction)'
    use_exit=f'{visible} && UiRecordContext.Key == {unassign} && {spouse}'
    exit_record=f'Filter(PlayersFaction.AvailableActionsList(true, {character}), {{UiRecordContext.Key == "{ACTION}"}}).FirstContext'
    for c in court.find('components'):
        for cb in c.findall('.//callback_with_context'):
            expr=cb.get('context_function_id','')
            kind=cb.get('callback_id')
            if c.get('id') in ('template_action','template_action_with_target') and kind is None and 'UiRecordContext.RequiresTarget' in expr:
                cb.set('context_function_id',f'({expr}) && UiRecordContext.Key != "{ACTION}" && GetIfElse({visible}, UiRecordContext.Key == {unassign}, true)')
            if kind=='ContextTextLabel' and expr=='ToUpper(UiRecordContext.LocalisedTitle)':
                cb.set('context_function_id',f'GetIfElse({visible} && UiRecordContext.Key == {unassign}, GetIfElse({spouse}, "休妻（移出后宫）", "移出后宫"), {expr})')
            if c.get('id')!='template_action':
                continue
            if kind=='ContextCommandLeftClick':
                confirmed=f'{panel}.ProcessCharacterAction(Component("252903D0-AA60-44DD-92942C5B8C2EAB3A").StoredContext("CcoCampaignGroupCharacterActionRecord"))'
                command=f'{panel}.ShowActionConfirmDialog({exit_record}, {character}, {confirmed})'
                cb.set('context_function_id',f'DoIfElse({use_exit}, {command}, {expr})')
            elif kind=='ContextInactiveStateSetter':
                cb.set('context_function_id',f'GetIfElse({use_exit}, {exit_record}.IsValidContext == true && {exit_record}.IsValidAction == true, {expr})')
            elif kind=='ContextPropagator' and '.PayloadInfoContext(this)' in expr:
                in_character=use_exit.replace('UiRecordContext.Key','StoredContext("CcoCampaignGroupCharacterActionRecord").UiRecordContext.Key')
                cb.set('context_function_id',f'GetIfElse({in_character}, {exit_record}.PayloadInfoContext(this), {expr})')
