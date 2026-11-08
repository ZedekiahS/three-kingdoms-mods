# 来源与许可

自有补丁生成器、诊断/校验脚本和文档按仓库根目录 MIT 许可。游戏原版内容、其他 Mod 内容及生成产物不因此获得 MIT 再授权。

| 参考 | 版本/文件 | 使用方式 |
|---|---|---|
| CA/SEGA 本机三国 | data.pack 的 family_court_panel、court_screen、court_screen_minister_slot、court_screen_info_lists、court_screen_imperial_court；database.pack 的职位、政治动作和 payload 表；原版 startpos | 专有资源，构建时从用户本机读取并适配；不提交完整提取物 |
| 原版家谱/确认框 | family_tree.twui.xml、dialog_action_confirmation.twui.xml；当前安装版本 | 研究 CharacterList、SpouseContext、原生确认和离婚动作，接口来自实际实现，不猜测 SDK |
| CA Assembly Kit 公告 | https://store.steampowered.com/news/posts/?appids=779340&enddate=1562592469 | 官方工具背景；没有找到完全匹配当前版本的公开 UI API 手册，以本机实现为依据 |
| Workshop 1970853594、3002004724 | 职位扩容 v13/v16；派系增益字段 v16 | 本地结构研究，找到人数上限和派系增益开关；没有发现开放源码许可，不上传其代码/数据 |
| Workshop 1989792160、3771244359 | 刘表太学职位改后宫，前者职位表 v9，后者 v13/v16 | 只借鉴复用原版职位的思路；不是全派系独立职位或真实婚姻的现成实现；无 LICENSE，不原样复制分发 |
| WH3-Mod-Manager / Shazbot | 既有 CAAB 读取器快照 `trait_readout/caabBinary.mjs` | MIT 衍生解析逻辑，保留 [许可](../LICENSES/WH3-Mod-Manager.txt)；不是原版三国官方 API |
| RPFM schemas / Frodo45127 | 本仓库 `schema_3k.ron` 快照；职位表 v13/v16 | MIT，保留 [许可](../LICENSES/rpfm-schemas.txt)。表读写逐字节往返，不假定所有游戏版本一样 |
| RPFM CAAB 文档 | https://frodo45127.github.io/rpfm/api/src/rpfm_lib/files/esf/caab.rs.html | 研究格式；最小写入器独立实现 |
| 7-Zip | 本机 26.02；DOC/7zFormat.txt、DOC/lzma.txt | 调用本机程序生成原生长度有界 LZMA 流，不分发可执行文件；依其自有许可 |

Workshop 链接及逐包结论见 [历史核查](reference-mods.md)。没有声称拥有第三方完整包的再分发权。源快照哈希见 `evidence/pause_snapshot.json`；上游精确 commit 未记录的部分，不冒充已锁定到维护中的最新版。
