> 历史调查记录；其中的当前状态、路径和版本可能已过期。以 [交接记录](HANDOFF.md) 为准。原版提取物未上传。

# 后宫原版府署复用核查

**2026-11-05 新证据：**用户下载后，已完整读取四个相关包并与本机原版逐表比对，见 [实际包核查](reference_mods/FINDINGS.md)。下文早先“未取得 pack”的记录保留为过程历史，已由新核查更新；纳娶 V1.51 仍未在本机找到。

核查时间：2026-11-04。先查实现、核实版本和授权，再改动；搜索不到不代表接口存在或不存在。

## 当前目标与失败证据

目标：复用原版府署页面、人物列表、职位卡片、效果提示和分阶段任职交互。后宫位于人物标签之后，独立职位为皇后 1、贵人 2、美人 3、宫人 3、采女 5。候选仅限本派系成年未婚女性。

本机 Three_Kingdoms.exe 文件及产品版本均为 **1.7.2.0**；主菜单显示 v1.7.1 Build 21463.3177261，记录这一区别，不把其他游戏的接口文档当作本机版本证据。

实际新建 190 曹操战役，原版府署正常，复制页无职位。自动诊断保存在 `debug_v1/native_post_probe_2026-11-04.log`：

- `character_posts()` 返回原版九类职位，没有任何 `syc_harem_*`。
- 新皇后职位 `GovermentPostForKey` 无有效上下文；原版丞相职位有效。
- 唯一女性卞夫人的 `IsEligibleForMarriage` 为 false，SpouseContext 有效；现有候选筛选错误。
- 结论：仅新增 DB 和 UI 没有在当前开局中创建实际职位。尚不能把原因进一步断言为某个 ESF 节点或缺失 API。

后续只读核查补充：从本机 `data.pack` 提取 190 历史模式 `startpos_historical.esf`，解压内层后完整遍历至节点区结束。原版确实在 `CAMPAIGN_STARTPOS/CAMPAIGN_ENV/CAMPAIGN_MODEL/WORLD/FACTION_ARRAY/FACTION/GOVERNMENT/CHARACTER_POSTS_CURRENT_GOVERNMENT/CHARACTER_POST` 中保存实际职位实例。原始文件 3,345,776 字节，解压内层 17,276,983 字节；职位记录摘录存于 `debug_v1/native_startpos_posts.json`。此检查证明开局文件持有职位实例，不证明自行插入记录即可安全工作。尚未写回、未替换任何 startpos；需要继续核对实例编号、政体切换记录及当前启用 Mod 的开局覆盖关系。

## 参考清单与使用边界

| 项目 | 版本 / 来源 | 文件或接口 | 许可证 / 使用决定 |
| --- | --- | --- | --- |
| Creative Assembly 本机原版 | 安装文件 1.7.2.0，直接提取的游戏资源 | `court_readout/vanilla/ui/campaign ui/family_court_panel.twui.xml`、`court_screen.twui.xml`、`court_screen_imperial_court.twui.xml`、`court_screen_minister_slot.twui.xml`、`court_screen_info_lists.twui.xml` | CA 专有游戏资源，不是开源许可证；当前仅用于用户本机 Mod 适配，不宣称获得独立再分发授权。直接复用原版控件，修改独立页面绑定、职位键、名称与候选条件。 |
| CA 本机 Lua 库 | 同一安装版本 | `court_readout/vanilla/script/_lib/lib_campaign_manager.lua`，`add_first_tick_callback` | 同上；诊断采用原版已存在的生命周期回调。 |
| 甲申之变本机包 `ming1644` | Workshop 3817018670；本地快照，没有核实作者版本号或当前上游 | `mod_readout/ming1644/text/script/campaign/3k_main_campaign_map/mod/ming_court_start.lua` | 在已提取文件中未找到明确许可证。仅研究调用方法；不能据此认定可复制发布。该文件使用既有职位及 `assign_to_post`，不是新增职位创建实例。 |
| 淝水之后本机包 `!rtz_era_384` | Workshop 3808594996；本地快照，没有核实作者版本号或当前上游 | `rtz_era_384.lua` 的 family_member / has_spouse；`rtz_era_384_events.lua` 的 character_posts 与 CampaignRoot 上下文查询 | 未找到明确许可证，限实现研究。用于核对只读诊断调用，不据此推导不存在的创建 API。 |
| Three Kingdoms Events & Interfaces 镜像 | https://chadvandy.github.io/tw_modding_resources/3k/scripting_doc.html ，非 CA 当前托管页面，精确补丁版本未注明 | QUERY_FACTION_SCRIPT_INTERFACE.character_posts；MODIFY_FACTION_SCRIPT_INTERFACE；角色 assign_to_post | 只作接口交叉核对；不能标为已验证的 1.7.2 官方完整文档。查阅部分尚未找到新增职位接口，不猜测函数名。 |
| Shazbot/WH3-Mod-Manager | https://github.com/Shazbot/WH3-Mod-Manager ，master 在线快照，尚未锁定提交 | `tools/esf/README.md`；工作区已有 `trait_readout/caabBinary.mjs` | 上游 MIT，Copyright (c) 2022 Shazbot。当前说明聚焦 WH3，不是三国职位创建实例；已有解析器本次只读遍历本机三国 startpos 成功。未用于写入或部署；改写或分发前需锁定版本并保留完整许可。 |

## 官方文档可用性

## 2026-11-05 同类 Mod 定向检索

以下已核对作者的 Steam Workshop 页面和公开元数据，**尚未取得 pack 源文件，不能当作源码验证**。

| 参考项目 | 作者 / 版本与日期 | 已确认的功能与相关性 | 源文件与许可状态 |
| --- | --- | --- | --- |
| [更多的称帝后官职](https://steamcommunity.com/sharedfiles/filedetails/?id=1970853594) | 姬昂の牛头人；说明标注 1.7；更新 2021-08-05 | 扩充官职数量、提前解锁官职。说明还写明未增加官职条目，因此不能据此断言它创建了独立职位种类。优先检查是否仅扩展已有职位名额。 | 公开 API 报告 724775 字节，但 file_url / filename 为空；未取得内部文件名。页面未见明确开源许可证，只能作为研究线索。 |
| [九卿派系加成 1.7.2](https://steamcommunity.com/sharedfiles/filedetails/?id=3002004724) | 闪闪绿藻头；标题 1.7.2；发布 2023-07-09 | 九卿启用人物派系加成，作者称玩家及 AI 生效、无需新档。与皇后/贵人的派系特性要求直接相关，但尚未核实具体表字段。 | API 报告 102347 字节，下载地址为空；内部文件名与许可证未核实。 |
| [纳娶：后宫 MOD V1.51](https://steamcommunity.com/workshop/filedetails/?id=2021724358&l=schinese) | hidde；V1.51；更新 2021-11-17 | 多配偶、人物面板按钮、家谱操作；不是作者已声明的独立府署页面实例。可研究婚姻状态与入口绑定，不能用其名称推定其实现等同于后宫官职。 | API 报告 3027017 字节，下载地址为空；内部文件名与许可证未核实。当前游戏补丁兼容性需验证。 |

下载尝试：Steam 公共详情接口成功返回三项元数据，但均无直接文件 URL。尝试打开 Steam 控制台后，Computer Use 读取客户端窗口返回 `window is minimized`，未能进入下载命令步骤。没有订阅、启用上述 Mod，没有替换游戏包。

本次能确认的是失效环节：原版 `court_screen.twui.xml` 通过 `GovermentPostForKey(self.Id)` 获取战役职位上下文，实际诊断中自定义 key 无上下文。完整创建路径仍需源码实例或官方工具验证；不得把 startpos 存在职位记录等同于已证明唯一修复方案。

本机没有 `assembly_kit` 目录。尝试访问 CA 三国 Mod 支持页面未成功；没有获得与本机补丁一一对应的官方职位创建说明。WH3 专属文档和已有 Napoleon ESF 脚本均不作为三国可调用接口的证据。

## 最小方案与未通过项

继续保留原版 UI 和原版任职流程。先找到并核实新增独立职位在开局数据中如何实例化，再决定最小数据改动；不能把后宫绑定到原有府署职位来假装成功，那会改动真实官职。

未婚条件应沿用原版 `IsEligibleForMarriage` 并验证候选数与实际婚姻状态一致。尚未部署此修复，避免把只改筛选描述成职位已修复。

后续验收必须同时满足：14 个后宫职位实际存在且显示；成年未婚女性筛选正确；第一次选位仅预览，确认后才任职；原府署不受影响；皇后和贵人启用人物派系增益、其他三类不启用。当前全部功能验收未通过，已安装包仍是诊断版。

## 2026-11-05 20:12 吕布独立职位：首次通过实际显示及任职

本节更新前面的调查状态；此前失败证据保留。最新包 SHA256：`2B3AD9812FF309348389539F98454D4EE16758D2F8BD6CC78857FFEBE2613191`。

- 根因已通过前后对照确认：仅将刘表太学的文化记录 faction_key 清空，不会为吕布生成战役职位实例。失败版有貂蝉候选，但无太学职位上下文。
- 按本机原版 `FACTION/GOVERNMENT/CHARACTER_POSTS_CURRENT_GOVERNMENT` 及 `CHARACTER_POSTS_OPPOSITE_GOVERNMENT` 的结构，在 194 演义吕布开局新增五类独立职位，各政体一份；保留全部原府署记录。全局职位编号计数的索引 15 是根据两份原版数据对照推断，并非已取得 CA 命名枚举文档。
- 五类职位最大并任人数为 1、2、3、3、5。复用原生多人职位列表，因此空岗显示一个“＋”入口，不是预画十四张空卡。
- 本机游戏 1.7.2.0 实际验证：五类全部显示，候选貂蝉可选；选择皇后空位进入原版预览，显示公共秩序 +2 和貂蝉的人物效果；点击确定后貂蝉担任皇后。切到普通府署再返回，任职仍在；普通官职、陈宫尚书令和吕姬储君均显示。
- 实际日志 `debug_v1/independent_five_lu_bu_runtime.log`：原有九个职位与五个 syc_harem 职位同时存在；皇后 HasPositionsAvailable 从 true 变 false；候选从 1 变 0（任职人物离开 NoblesCharacterList）。这验证了皇后单人上限，不等于已经验证所有多人上限。
- 生成器 `build_lu_bu_test.py` 与 `patch_native_posts.mjs` 已通过：原文件无修改往返字节相同、原有职位和其他派系记录字节相同、新 ID 唯一、封装后完整解压字节相同、包内数据回读及原生 UI 差异检查。
- 目前安装的是 **194 演义吕布新战役测试包**；不是全派系/全剧本版，不会为已有存档补职位。没有实现婚姻，没有验证多人满员、实际增益结算、称帝切换和存档读回。预览文字保留原版特性条件，尚不能仅凭文字断言结算已正确。

本次补充的格式参考和工具：

| 来源 | 版本与文件 | 使用与许可 |
| --- | --- | --- |
| RPFM | 在线 master 文档，`rpfm_lib/files/esf/caab.rs`；https://frodo45127.github.io/rpfm/api/src/rpfm_lib/files/esf/caab.rs.html | MIT；研究 CAAB 记录长度、字符串表和压缩外壳格式，没有复制写入器源码。与本机三国实际数据往返核对。 |
| ip7z/7zip | `DOC/7zFormat.txt` 格式说明 18.06；`DOC/lzma.txt` 24.07；https://github.com/ip7z/7zip | 研究格式，从已安装 7-Zip 26.02 的单文件 LZMA 归档取得不带结束标记的压缩流；不复制或分发其程序源码。安装目录 License.txt：主 LGPL，部分库另有 BSD/unRAR 条款。 |
| 本机既有 CAAB 读取器 | `trait_readout/caabBinary.mjs`，原有 WH3-Mod-Manager 衍生文件 | 沿用现有读取接口；本次写入器是围绕本机三国结构的最小适配，未引入新的 Mod API。上游 MIT 与版本限制见上文。 |

压缩失败也保留其原因：Python FORMAT_ALONE 生成带结束标记的流；直接改为原生已知长度头在当前解码器报错。改用现有 7-Zip 输出后，原生外壳完整回读成功，且游戏成功进入新战役。没有通过截断或修改未知压缩字节绕过校验。
