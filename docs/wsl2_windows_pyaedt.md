# WSL2 调用 Windows HFSS / PyAEDT

当前机器已经验证以下链路可用：

```text
WSL2 -> Windows python.exe -> PyAEDT 1.6.0 -> AEDT 2025.2 Student
```

Windows PyAEDT 环境由 AEDT 安装器创建，位置是：

```text
C:\Users\chaoy\AppData\Roaming\.pyaedt_env\3_10\Scripts\python.exe
```

## WSL2 中运行

```bash
chmod +x scripts/wsl_pyaedt_launcher.sh
scripts/wsl_pyaedt_launcher.sh --check
scripts/wsl_pyaedt_launcher.sh --hfss-smoke
scripts/wsl_pyaedt_launcher.sh --hfss-gui-demo
```

`--hfss-gui-demo` 会让 Windows AEDT 打开 GUI，创建一个 WR90 尺寸的双脊波导
基础几何，并保存为 `C:\Users\<用户名>\Documents\wsl_hfss_gui_demo.aedt`。
Python 文件仍然在 WSL 的 `scripts/hfss_gui_draw_demo.py` 中编辑；回到 WSL
终端按 Enter 后脚本才会关闭 AEDT 会话。

也可以指定工程输出路径：

```bash
HFSS_PROJECT_PATH='C:\\Users\\chaoy\\Documents\\my_model.aedt' \\
  scripts/wsl_pyaedt_launcher.sh --hfss-gui-demo
```

如果 Student 版在无图形模式下卡在 `Inserting a new design`，让 Windows AEDT
使用图形界面启动：

```bash
AEDT_NON_GRAPHICAL=0 scripts/wsl_pyaedt_launcher.sh --hfss-smoke
```

运行自己的脚本：

```bash
scripts/wsl_pyaedt_launcher.sh scripts/your_hfss_script.py
```

当前 PyAEDT 版本使用 `new_desktop=True`，不要使用旧示例中的
`new_desktop_session=True`。

## 如果出现 `UtilBindVsockAnyPort` 或无法运行 Windows 程序

在 Windows PowerShell 中执行：

```powershell
wsl --shutdown
```

重新打开 Ubuntu 后检查：

```bash
echo "$WSL_INTEROP"
cmd.exe /c ver
```

如果 `cmd.exe /c ver` 仍失败，再执行：

```powershell
wsl --update
```
