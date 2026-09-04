# Guitar Learning Assistant · 开源预备版

这是一个便于体验和审阅的预备发布包，工程代码、内置曲库、测试和文档位于同一目录。

## 无代码运行

Windows 用户无需安装 Python：

1. 保持整个 `GuitarLearningAssistant` 文件夹完整（包括 `_internal` 子目录），不要只复制 `.exe`。
2. 双击根目录的 `start.bat`，或直接运行 `GuitarLearningAssistant\\GuitarLearningAssistant.exe`。
3. 首次启动后可在界面中切换中英文、选择曲目并播放音频。

## 源码运行

安装 `requirements.txt` 中的依赖后执行 `python main_window.py`。详细操作请参阅 `USER_GUIDE.md`。

## 当前预备版提示

- 内置曲目用于演示；其中部分音频是 MIDI 合成测试音频。源码曲库位于根目录 `songs/`，EXE 运行时的曲库位于 `GuitarLearningAssistant\\_internal\\songs\\`。发布前请核对每个 `songs/*/info.json` 的来源与授权。
- 刻度、谱面行识别和音频同步适用于常见清晰谱面，但复杂排版、扫描倾斜、装饰符号可能需要手动校正。
- 曲库删除会直接移除对应曲目文件夹，操作不可恢复，请先备份。
- `LICENSE` 和 `AUTHOR_CONTACT.txt` 中的 `AUTHOR_EMAIL@example.com` 是占位符，公开发布前必须替换成真实邮箱。
- `LICENSE-MIT.txt` 与 `LICENSE-APACHE.txt` 是两个可选的正式许可证模板，发布原创代码时应二选一，并把其中的 `AUTHOR_NAME` 替换为实际版权所有者。
- 当前 `LICENSE` 是项目的非商业发布声明，不替代正式许可证；第三方曲谱、音频、MIDI、字体等内容仍须遵循各自授权，不能直接套用 MIT 或 Apache-2.0。
