-- Native family/appointment interfaces, checked against local rtz/ming usage
-- and the CA-generated 3K interface documentation mirror. No marriage edits.
local function syc_initialise_spouse_queen()
 local faction=cm:query_faction(cm:get_local_faction(true))
 if faction:is_null_interface() then return end
 local queen=nil
 local posts=faction:character_posts()
 for i=0,posts:num_items()-1 do
  local post=posts:item_at(i)
  if post:ministerial_position_record_key()=='syc_harem_queen_1' then queen=post;break end
 end
 if not queen then return end -- This campaign must actually contain our posts.
 local leader=faction:faction_leader()
 if leader:is_null_interface() or leader:is_dead() then return end
 local family=leader:family_member()
 if family:is_null_interface() or not family:has_spouse() then return end
 local spouse_family=family:spouse()
 local spouse=spouse_family:character()
 if spouse:is_null_interface() or spouse:is_dead() or spouse:is_male()
  or not spouse_family:come_of_age() or spouse:age()<18
  or spouse:faction():name()~=faction:name() then return end
 local marker='syc_spouse_queen_v1_'..faction:name()..'_'..leader:cqi()..'_'..spouse:cqi()
 if cm:get_saved_value(marker) then return end
 -- Once per couple: never overwrite a queen or undo a player's later removal.
 if queen:current_post_holders()>0 then
  cm:set_saved_value(marker,true)
  ModLog('[SYC SPOUSE] existing queen retained; spouse available for manual appointment')
  return
 end
 local current=spouse:character_post()
 if not current:is_null_interface() and current:ministerial_position_record_key()~='' then
  cm:set_saved_value(marker,true)
  ModLog('[SYC SPOUSE] existing spouse office retained')
  return
 end
 cm:modify_character(spouse):assign_to_post('syc_harem_queen_1')
 cm:callback(function()
  local result=spouse:character_post()
  if not result:is_null_interface() and result:ministerial_position_record_key()=='syc_harem_queen_1' then
   cm:set_saved_value(marker,true)
   ModLog('[SYC SPOUSE] queen assigned: '..spouse:generation_template_key())
  else
   ModLog('[SYC SPOUSE] ERROR: queen assignment did not take effect')
  end
 end,0.2)
end
