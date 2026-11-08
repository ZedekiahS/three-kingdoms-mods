> 历史调查记录；其中的当前状态、路径和版本可能已过期。以 [交接记录](HANDOFF.md) 为准。原版提取物未上传。

# 配偶改封与退出后宫（2026-11-08）

## 规则

- 改封：通过原版人物选择、职位预览、二次点击确认，把同一人移到其他后宫名位；婚姻保持。
- 当前君主配偶退出后宫：显示“休妻（移出后宫）”，原版确认后同时解除婚姻与名位，保留原版离婚费用和关系后果。
- 尚未实际结婚的任职人物：显示“移出后宫”，仅撤销名位。现有多名位系统不等于引擎已支持多人婚姻。
- 女儿等亲属可以查看，不可任职；君主现任成年女性配偶是已婚资格的例外。

## 版本、参考与许可

本次实际启动菜单为 v1.7.1 Build 1246.377261，程序错误记录文件版本 1.7.1.0。此前笔记的 1.7.2.0 不能代替当前运行证据。以本机 data.pack、database.pack 的实现为准。

1. `court_readout/vanilla/ui/campaign ui/family_court_panel.twui.xml`：保留原始 AvailableActionsList 与原生操作模板；只在后宫页面改造撤位按钮的有效性、提示和确认目标。
2. `research_spouse/ui/campaign ui/family_tree.twui.xml`：CharacterList 包含家族人物，府署 NoblesCharacterList 不包含全部配偶；参考其完整人物来源。
3. `database.pack`：沿用原版 divorce 动作的条件、费用、关系效果，复制为独立 action/payload；在同一 payload 加入原版 unassign_from_post 组件及提示效果。一次确认执行一次 payload，避免先撤位导致确认上下文丢失。
4. 原版对话框 `research_kinship/dialog_action_confirmation.twui.xml`、原版 minister slot：保留确认/取消、原生改封流程。
5. 已下载后宫/学校参考 Mod：见 `../reference_mods/FINDINGS.md`。没有找到其实际婚姻退出实现或可直接复用许可，因此本次未复制第三方源码。
6. CA 官方 Assembly Kit 公告：https://store.steampowered.com/news/posts/?appids=779340&enddate=1562592469 。未找到与当前版本完全匹配的公开 UI 接口说明；本机原版文件是此次接口依据。CA 生成的脚本文档镜像用于核对现有 assign_to_post，不推测未公开的离婚脚本接口。

原版文件版权属于 CA/SEGA；本地适配，不主张开源许可，不新增公开分发授权。

## 已定位问题

- 原生撤位不会离婚：实测家谱离婚后婚姻解除，但皇后职位仍在；单独撤位则皇后空缺、婚姻仍在。
- 配偶来源：运行日志显示 CharacterList 有 9 人、女性 2 人；NoblesCharacterList 女性仅 1 人。冯夫人已婚且满足成年、存活、未放逐及现任君主配偶条件。
- 配偶筛选上下文：`Filter(... IsContextValid(SpouseContext) ...)` 的全局函数参数解析到 CcoStaticObject，运行日志明确报 SpouseContext 不存在。使用 `(x) => ... IsContextValid(x.SpouseContext)` 显式绑定人物，不能仅用 Python 布尔夹具证明引擎表达式有效。原失败日志保存在 `../debug_v1/spouse_filter_context_failure.log`。
- 早期修改整个 actions_list 的版本在载入时崩溃，已保留失败实现 `../debug_v1/failed_action_list_patch.py`。当前保留原始 actions_list 不动。

## 验证

- 结构检查：原生操作列表保持不变；非后宫保留原版按钮执行分支；14 个固定格子、任职限制、XML 引用及包回读通过。
- 数据检查：退出 payload 含 divorce 与 unassign_from_post；原版离婚交易保留；10 份 startpos 字节不变。差异记录 `../debug_v1/spouse_roster_package_diff.json`。
- 实机验收待补充：配偶列表、改封不离婚、退出同时解除婚姻与名位、取消不生效、普通府署原操作。

本轮使用临时 190 袁术新局，没有覆盖用户存档；保存按钮灰色，未声称已完成保存/读档验证。
