# VibeType

[English](README.md) | 简体中文

基于 `iic/SenseVoiceSmall` 的桌面端语音转文字工具。

## 文件说明

- `install-deps.bat`：在 Windows 上创建 `.venv` 并安装依赖
- `install-deps.sh`：在 Linux/macOS 上创建 `.venv` 并安装依赖
- `start.bat`：在 Windows 上启动桌面应用
- `start.sh`：在 Linux/macOS 上启动桌面应用
- `start-hotkey.bat`：与 `start.bat` 相同
- `start-hotkey.sh`：与 `start.sh` 相同

## 使用方法

### Windows

1. 首次运行 `install-deps.bat`
2. 运行 `start.bat`
3. 将光标聚焦到任意输入框
4. 按 `Ctrl+Shift+Space` 开始录音
5. 再按一次 `Ctrl+Shift+Space` 停止并自动输入识别结果

### Linux/macOS

1. 运行 `chmod +x install-deps.sh start.sh start-hotkey.sh`
2. 首次运行 `./install-deps.sh`
3. 运行 `./start.sh`
4. 将光标聚焦到任意输入框
5. 按 `Ctrl+Shift+Space` 开始录音
6. 再按一次 `Ctrl+Shift+Space` 停止并自动输入识别结果

## 说明

- 默认识别语言为中文（`zh`）
- 卡片式桌面界面
- 实时麦克风电平显示
- 最近识别历史列表
- 支持窗口“置顶”
- 支持“停止后最小化到后台”
- 如需强制重装依赖：
  - Windows：`start.bat install`
  - Linux/macOS：`./start.sh install`
- 若在 Windows 管理员权限窗口中热键无效，请也以管理员权限运行本应用
