# 从本机游戏重建

需要 Python 3.11+、Node.js 22+、已安装的 7-Zip，以及合法安装的《全面战争：三国》。使用 Python/Node 标准库，不需要新增 npm 依赖。源码保留原目录结构，避免改动游戏逻辑。

在仓库 `mods/inner-palace` 内执行：

```powershell
python tools/rebuild.py --game-data 'C:/Program Files (x86)/Steam/steamapps/common/Total War THREE KINGDOMS/data' --sevenzip 'C:/Program Files/7-Zip/7z.exe'
```

构建从本机 data.pack 提取所需 5 个原版 UI，从 database.pack 读取职位/动作和文化数据，从 data.pack、fast.pack 读取 10 份开局，生成全汉文化固定格子候选。输入包与产物哈希写到本地 `dist/build_receipt.json`。

输出：`work/prototypes/inner-palace/zz_syc_harem_fixed_fourteen.pack`。**候选尚未完成按钮/婚姻实机验收；脚本不会安装、启动游戏或更改存档。** 如果已有非空 `fixed_fourteen_src`，工具拒绝覆盖，避免旧实验文件混进新包；在新工作副本构建或自行备份、清理生成目录。

生成后的独立检查：

```powershell
$env:TW3K_DATA='C:/Program Files (x86)/Steam/steamapps/common/Total War THREE KINGDOMS/data'
python work/prototypes/inner-palace/verify_court_copy.py --fixed-slots
python work/prototypes/inner-palace/verify_spouse_roster.py
python work/prototypes/inner-palace/verify_appointment_guard.py work/prototypes/inner-palace/fixed_fourteen_src/ui/syc_harem_native/minister_slot.twui.xml
```

安装需先退出游戏、备份现有后宫包，再经明确授权替换到 data 下的 `zz_syc_harem_preview_v2.pack`。不要同时启用旧后宫包和新包。当前是 movie 类型包，放入 data 就可能自动加载；停用要把文件移出 data。本次暂停上传不执行安装。

新职位依赖开局实例，已有无职位的存档不会因安装自动获得职位；不改存档。已含职位的存档是否可安全接受后续动作改造，需保存/读回实测。其他覆盖相同开局或 family_court_panel 的 Mod 需要专门合并。

所有提取物、pack、ESF、数据库与生成的完整 UI 均在忽略目录，不得作为自有源码提交。重建成功只证明本地包结构通过，不证明游戏行为或其他版本兼容。

2026-11-08 导出验证：从此子目录的干净生成目录重建 10 份开局并通过上述检查，所得包与暂停时未验收候选逐字节哈希一致，大小 23,603,235 字节。记录见 [export_validation.json](evidence/export_validation.json)。本次未执行游戏安装或实机测试。
