# 全面战争：三国 · Mod 实验合集

集中保存《全面战争：三国》的 Mod 源码、素材、构建方法和开发复盘。各个 Mod 放在独立目录，分别说明安装方式、依赖、当前状态和兼容范围。

## 项目目录

| 目录 | 内容 | 当前状态 |
|---|---|---|
| [mods/portraits](mods/portraits/) | 原版 / MTU 3.3 立绘实验补丁 | 已上传源码、27 人原画和故障复盘；三人局部游戏验证，画风与专属护甲未完成 |

机制 Mod 将后续单独放入 `mods/` 下的新目录；目前尚未上传。合集中的项目不代表可以全部同时启用，兼容性以各自说明和实际测试为准。

## 获取与使用

```powershell
git clone https://github.com/ZedekiahS/three-kingdoms-mods.git
cd three-kingdoms-mods
```

然后进入所需 Mod 的目录，按照该目录的 README 操作。立绘项目的构建命令需要在 `mods/portraits` 中执行。

- [立绘现状与构建入口](mods/portraits/README.md)
- [立绘故障完整复盘：重叠、不显示、头像裁切等](mods/portraits/docs/TROUBLESHOOTING.md)
- [立绘换电脑恢复与安装](mods/portraits/docs/INSTALL.md)

原仓库名为 `three-kingdoms-portrait-mod`，现改为 `three-kingdoms-mods`。已有克隆可在仓库根目录执行：

```powershell
git remote set-url origin https://github.com/ZedekiahS/three-kingdoms-mods.git
git pull --ff-only
cd mods/portraits
```

旧克隆中的未跟踪构建产物和依赖不会随 Git 自动迁移；在新子目录按项目文档重新构建即可。

本仓库自有代码和文档采用 [MIT](LICENSE)。图片及第三方内容遵守各子项目的许可说明；游戏或其他 Mod 的原始素材不因本仓库开源而重新授权。
