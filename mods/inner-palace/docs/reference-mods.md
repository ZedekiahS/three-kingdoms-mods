> 历史调查记录；其中的当前状态、路径和版本可能已过期。以 [交接记录](HANDOFF.md) 为准。原版提取物未上传。

# 已下载职位 Mod 实际包核查

日期：2026-11-05。本次只读源包并提取研究副本，没有启用 Mod、替换游戏包或修改存档。

## 核查范围与证据

在 Steam 唯一游戏库的 `workshop/content/779340` 找到四个相关包。全量索引、原始条目、解码 JSON、逐表差异位于本目录各 Workshop ID 子目录。每包 `manifest.json` 保存原始绝对路径、SHA-256、Steam 更新时间和下载 manifest。

六个 DB 文件共 595 行全部解码到文件末尾，并重新编码得到逐字节相同内容；两个本地化文件共 20 行完整解析。不是仅从作者页面推测。差异按职位键或文化/派系/职位/子文化/战役复合键匹配本机原版数据；旧 schema 中已经移除的字段明确标记，不能当作当前接口。

| Workshop ID / 包 | 实际内容 | 结论 |
| --- | --- | --- |
| 1970853594 / `ddd.pack` | 仅两张表：`ministerial_positions_tables/data`（v13，59 行）、`ministerial_positions_culture_details_tables/data`（v16，154 行） | 全部职位键均来自原版。7 个职位的 `maximum_concurrent_ministers` 从 1 改为 3，102 条文化记录的派系进度门槛降低到 1；另有年龄调整。没有 Lua、UI、startpos 或新职位类别。 |
| 3002004724 / `factionwide_effects_for_all_ministers.pack` | 文化细节表 v16，168 行；另两份空白/编辑器设置文件 | 94 条记录将 `allow_character_to_factionwide_ministerial_effects` 从 false 改为 true。包括刘表的三个太学职位。没有修改效果数值表，也没有通过脚本累加增益。 |
| 1989792160 / `liubiao.pack` | 职位表 v9，6 行；`text/A.loc` 10 行 | 沿用刘表 scholar/tutor/student，分别命名为美人/夫人/贵人，各 3 名；调整年龄，同时改了其他已有职位。v9 与本机 v13 不同，不能原样复制旧格式。 |
| 3771244359 / `liubiaopark.pack` | 职位表 v13，54 行；文化细节表 v16，154 行；`text/A.loc` 10 行；编辑器元数据 | 沿用刘表 tutor=皇后 1、scholar=贵妃 3、student=嫔妃 9；另外扩容了丞相、储君等既有官职。包内没有新界面、Lua 或 startpos。 |

## 刘表后宫如何沿用原版

原版 `court_readout/vanilla/ui/campaign ui/court_screen_3k_main_faction_liu_biao.twui.xml` 已有三个太学职位容器（约 113–231 行），用 `GovermentPostForKey(self.Id)` 获取原版职位，再创建 `court_screen_minister_slot`。上述两包保留这些 key，仅改数据和本地化，因此继续使用原版府署的布局、人物列表及任职操作。

原版 `court_screen_minister_slot.twui.xml` 的关键现成逻辑：

- 211 行：`CourtScreenStagedSlot`；219 行：原生 `AssignCharacter` 与 `ClearSelectedSlot`。
- 2030 行：`PostEffectList(...) + CharacterEffectList(...)`，合并职位与人物效果。
- 5620–5622 行：`ContextList / CharacterList`；5643 行：`HorizontalList`，列出同职多人。
- 5984 行：`HasPositionsAvailable` 控制还有无空位。

因此人数上限通过 `maximum_concurrent_ministers` 设置，已任职人物由原生列表呈现，不需要手绘一套名额和确认弹窗。这也不等于原版会预先把全部上限画成多个空框。

## 对当前后宫的直接意义

1. 皇后/贵人开启人物派系增益，有现成字段和已下载实例支持；其余三类保持关闭。仍需检查实战结算及重复计入情况。
2. 当前自定义 `syc_harem_*` 无战役职位上下文的诊断依然成立；这四包都复用原版 key，**没有任何一个证明新 key 会自动创建实际职位**。不能再把新增 DB 条目等同于新增运行时职位。
3. 最小可验证路线：先沿用原版刘表太学职位及完整卡片，核实名额、效果预览、确认任职和婚姻筛选，再解决独立页面所需的职位来源。此处只提出验证顺序，本次没有更换实现，也没有占用原府署职位冒充独立职位。
4. 刘表只有三个太学职位类别，用户需求是五类、14 名且保留正常府署。直接复制这个 Mod 不能自动满足后两项，更不能据此保证曹操或原创派系可用。
5. 两个后宫包均未加入女性/未婚限制或婚姻脚本；不能把其名称视为筛选、婚姻功能已经实现。
6. `liubiaopark` 三个太学记录仍把人物派系增益设为 false；与九卿增益包存在同键不同值，加载覆盖可能影响结果。它还保留 tutor 的 `character_rank_requirement=66`，需要结合原版具体规则验证，不能只看年龄表就认定任职条件已放开。

## 版本、许可与未取得内容

- 本机 EXE 版本 1.7.2.0。三个较新包使用与本机匹配的相关 DB schema 版本（v13/v16）；这只证明数据结构可读，不代表本次完成游戏内兼容验收。
- 作者：官职扩展为姬昂の牛头人；九卿加成为闪闪绿藻头（前次作者页核查）。3771244359 为 base（用户提供作者页截图）；1989792160 的作者身份本次未独立核实。
- 四个包中没有 LICENSE 文件；两个含 RPFM notes 的包均未写许可说明。本次仅本地研究。后续基于本机原版数据自行制作最小差异，不能把下载权限当作外部代码/文本的再分发授权。
- Workshop 2021724358（纳娶 V1.51）没有出现在本机内容目录或安装清单，游戏 data 目录也未找到对应文件。本次没有读到它的源码，不能列作已检查。
- 本次尝试在线访问两个刘表 Mod 页面失败；功能结论来自实际包，页面信息仅在用户提供的截图范围内使用。没有根据访问失败推断 Mod 已删除。

来源页：<https://steamcommunity.com/sharedfiles/filedetails/?id=1970853594>、<https://steamcommunity.com/sharedfiles/filedetails/?id=3002004724>、<https://steamcommunity.com/sharedfiles/filedetails/?id=1989792160>、<https://steamcommunity.com/sharedfiles/filedetails/?id=3771244359>。
