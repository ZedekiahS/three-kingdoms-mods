# 结构、参考与重建

保留原实验脚本的相对目录结构，减少迁移时导入路径变化。统一入口是 `tools/rebuild.py`，不要按文件名猜执行顺序。

| 路径 | 作用 |
|---|---|
| `character_art/` | 自己生成的原画和未采用的吕蒙风格试稿 |
| `work/prototypes/portrait-pack/characters.json` | 27 人的真实模板、私有美术编号和源图映射 |
| `prepare_assets.cjs` | 旧实验底包导出，保留用于复现；不代表适配完整 |
| `build.py` | PFH5 输出、人物 DB 绑定、开局美术引用修改 |
| `generic_route_probe.py` | 鲁肃/韩当的泛型路径修复和透明装备占位 |
| `fix_bobbleheads.cjs` | 原版府署裁切下的头像定位；`--lu-meng` 为吕蒙 |
| `add_lu_meng.py` | 保留前两人修复字节不变，加入吕蒙资源 |
| `character_audit/` | DB 解码、开局解析辅助；生成数据不入库 |
| `trait_readout/caabBinary.mjs`、`caabOffsets.mjs` | CAAB 读取与偏移支持，源于 MIT 上游的本地适配 |
| `work/prototypes/inner-palace/` | 仅保留共享 DB 读写与压缩外壳工具；不含后宫功能 |
| `schema_3k.ron` | MIT RPFM schema 快照 |

新电脑重建流程：读取本地包目录和目标原版头像 -> 导出旧实验底包 -> 生成原版/MTU两份绑定 -> 修复鲁肃/韩当 -> 对齐府署头像 -> 增加吕蒙 -> 输出四包和哈希。仍只有三人适配后的局部实验结果，入口没有偷偷把剩余24人宣布完成。

重建保留三表绑定与8份目标开局美术引用的旧策略，不写 CEO、游戏脚本、属性、技能、物品或中文本地化。与其他覆盖同一 startpos 的 Mod 是否兼容，需检查实际文件，不是按 Mod 名字推断。

## 参考来源

- [Custom Character Creation，Zades](https://steamcommunity.com/sharedfiles/filedetails/?id=1798650568)：泛型 faces、透明装备占位和 PNG Comment 的作者说明。
- [本轮查阅的立绘修复模组页面](https://steamcommunity.com/sharedfiles/filedetails/?id=3679748482)：作者的缺失立绘路径修复经验。
- [MTU](https://steamcommunity.com/sharedfiles/filedetails/?id=1812159400)：本机3.3包；真实人物绑定、CEO内容及图片路径优先于网页名单。
- [淝水之后](https://steamcommunity.com/sharedfiles/filedetails/?id=3808594996)、[甲申之变](https://steamcommunity.com/sharedfiles/filedetails/?id=3817018670)：只读研究本机人物->美术->faces结构，不分发其资源。
- [WH3-Mod-Manager](https://github.com/Shazbot/WH3-Mod-Manager)：CAAB读写相关格式参考/解析器来源，MIT。三国尺寸字段做了本地适配，不能无条件套用WH3假设。
- [RPFM schemas](https://github.com/Frodo45127/rpfm-schemas) 与 [RPFM](https://github.com/Frodo45127/rpfm)：DB版本/字段及ESF格式参考，MIT。
- [7-Zip](https://github.com/ip7z/7zip)：读取格式说明并调用本机程序，不附带其二进制。

上游链接不代表本仓库获得各游戏/模组的整体授权。许可快照提交及限制详见 `LICENSES/provenance.json` 和许可文档。历史适配代码最初对应的准确上游提交未能恢复，已如实注明；本仓库本身提交固定了当前工作副本。
