local function log(s)if ModLog then ModLog('[SYC NATIVE CHECK] '..tostring(s))end end
local function inspect()
 local ok,err=pcall(function()
  local f=cm:query_faction(cm:get_local_faction(true));local ps=f:character_posts();local keys={}
  for i=0,ps:num_items()-1 do keys[#keys+1]=ps:item_at(i):ministerial_position_record_key()end
  log('posts: '..table.concat(keys,','))
  local expressions={
   'PlayersFaction.CharacterList.Size',
   'PlayersFaction.CharacterList.Filter((x) => x.IsMale == false && (x.IsEligibleForMarriage || (IsContextValid(x.SpouseContext) && x.SpouseContext.IsFactionLeader && x.SpouseContext.FactionContext.IsPlayersFaction))).Size',
   'PlayersFaction.IsPlayersFaction',
   'PlayersFaction.CharacterList.Filter(IsMale == false && IsContextValid(SpouseContext)).Size',
   'PlayersFaction.CharacterList.Filter(IsMale == false && SpouseContext.IsFactionLeader).Size',
   'PlayersFaction.CharacterList.Filter(IsMale == false && SpouseContext.FactionContext.IsPlayersFaction).Size',
   'PlayersFaction.CharacterList.Filter(IsMale == false && (IsEligibleForMarriage || (IsContextValid(SpouseContext) && SpouseContext.IsFactionLeader && SpouseContext.FactionContext.IsPlayersFaction))).Size',
   'PlayersFaction.CharacterList.Filter(IsMale == false).Size',
   'PlayersFaction.CharacterList.Filter(IsMale == false && IsEligibleForMarriage == false).Size',
   'IsContextValid(PlayersFaction.FactionLeaderContext.SpouseContext)',
   'PlayersFaction.FactionLeaderContext.SpouseContext.IsMale',
   'PlayersFaction.FactionLeaderContext.SpouseContext.ComeOfAge',
   'PlayersFaction.FactionLeaderContext.SpouseContext.IsAlive',
   'PlayersFaction.FactionLeaderContext.SpouseContext.IsBanished',
   'PlayersFaction.FactionLeaderContext.SpouseContext.IsTemporaryCommander',
   'PlayersFaction.FactionLeaderContext.SpouseContext.SpouseContext.IsFactionLeader',
   'PlayersFaction.FactionLeaderContext.SpouseContext.SpouseContext.FactionContext.IsPlayersFaction',
   'PlayersFaction.NoblesCharacterList.Size',
   'PlayersFaction.NoblesCharacterList.Filter(IsMale == false).Size',
   'PlayersFaction.NoblesCharacterList.Filter(IsMale == false && ComeOfAge).Size',
   'PlayersFaction.NoblesCharacterList.Filter(IsTemporaryCommander == false && ComeOfAge && IsMale == false && IsEligibleForMarriage).Size',
   'PlayersFaction.NoblesCharacterList.Filter(IsMale == false).FirstContext.IsEligibleForMarriage',
   'IsContextValid(PlayersFaction.NoblesCharacterList.Filter(IsMale == false).FirstContext.SpouseContext)',
   'IsContextValid(PlayersFaction.GovermentPostForKey("syc_harem_queen_1"))',
   'PlayersFaction.GovermentPostForKey("syc_harem_queen_1").HasPositionsAvailable',
   'PlayersFaction.GovermentPostForKey("3k_main_court_offices_prime_minister").HasPositionsAvailable'
  }
  local root='CampaignRoot.FactionList.Filter((x) => x.FactionRecordContext.Key == '..string.format('%q',cm:get_local_faction(true))..').FirstContext'
  for _,e in ipairs(expressions)do e=string.gsub(e,'%f[%a]PlayersFaction%f[%A]',root);local success,v=pcall(function()return effect.get_context_value(e)end);log(e..' => '..tostring(success)..' '..tostring(v))end
 end)
 if not ok then log(err)end
end
function syc_harem_preview()
 cm:add_first_tick_callback(inspect)
 core:add_listener('syc_native_check','ComponentLClickUp',function(ctx)return UIComponent(ctx.component):Id()=='syc_harem_native_open'end,function()
  log('tab clicked');inspect()
 end,true)
 log('diagnostic loaded')
end
