"""Adapt the local 1.7.2 family/court action list, without new action APIs."""
def patch_actions(court, pageid, postkeys):
    visible=f'Component("{pageid}").IsVisible'
    selected='StoredContext("CcoCampaignCharacter")'
    own_post='('+' || '.join(f'{selected}.GovermentPostContext == PlayersFaction.GovermentPostForKey("{key}")' for key in postkeys)+')'
    spouse=f'(IsContextValid({selected}.SpouseContext) && {selected}.SpouseContext.IsFactionLeader && {selected}.SpouseContext.FactionContext.IsPlayersFaction)'
    unassign='"3k_main_campaign_group_political_action_unassign_from_post"'
    divorce='"3k_main_campaign_group_political_action_divorce"'
    for c in court.find('components'):
        for cb in c.findall('.//callback_with_context'):
            expr=cb.get('context_function_id','')
            if c.get('id')=='actions_list' and cb.get('callback_id')=='ContextList':
                harem=f'Filter(AvailableActionsList(false, {selected}), {{UiRecordContext.Key == {unassign}}})'
                family=f'Filter(AvailableActionsList(true, {selected}), {{UiRecordContext.Key == {divorce}}})'
                # Married spouses get only the combined exit action. An unmarried
                # holder has no engine marriage to dissolve, so only leaves office.
                # GetIf is a nullable single-context operation in the native UI.
                # List callbacks must return a list in both branches, as in
                # family_tree.twui.xml HorizontalList.
                empty=f'Filter(AvailableActionsList(false, {selected}), {{false}})'
                harem=f'GetIfElse({spouse}, {family}, GetIfElse({own_post}, {harem}, {empty}))'
                cb.set('context_function_id',f'GetIfElse({visible}, {harem}, {expr})')
            if cb.get('callback_id')=='ContextTextLabel' and expr=='ToUpper(UiRecordContext.LocalisedTitle)':
                label=f'GetIfElse(UiRecordContext.Key == {unassign}, "移出后宫", GetIfElse(UiRecordContext.Key == {divorce}, "休妻（移出后宫）", {expr}))'
                cb.set('context_function_id',f'GetIfElse({visible}, {label}, {expr})')
            if cb.get('callback_id')=='ContextCommandLeftClick' and 'ShowActionConfirmDialog' in expr:
                panel='Component("F49F83BC-0CEE-4BCE-8DE2EA61AB8D5B39")'
                record='Component("252903D0-AA60-44DD-92942C5B8C2EAB3A").StoredContext("CcoCampaignGroupCharacterActionRecord")'
                character='Component("BB52800B-3C9A-4DB8-B3346DDBDDEAC443").StoredContext("CcoCampaignCharacter")'
                release=f'Filter(PlayersFaction.AvailableActionsList(false, {character}), {{UiRecordContext.Key == {unassign}}}).FirstContext'
                confirmed=f'{panel}.ProcessCharacterAction({record})'
                own=own_post.replace(selected,character)
                # CA's Do(...) sequences existing commands. Only the confirmed
                # harem divorce path also issues the native unassign operation.
                combined=f'DoIfElse({visible} && {record}.UiRecordContext.Key == {divorce} && {own}, Do({panel}.ProcessCharacterAction({release}), {confirmed}), {confirmed})'
                assert confirmed in expr
                cb.set('context_function_id',expr.replace(confirmed,combined))
