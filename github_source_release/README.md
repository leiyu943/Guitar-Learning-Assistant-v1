# 吉他学习助手 / Guitar Learning Assistant

这是一个面向古典吉他练习的 PyQt6 桌面工作台。当前版本来自原项目归档后的安全恢复与持续开发，重点是“谱面 + 音频 + 可定位播放”的本地练习流程。

This is a PyQt6 desktop practice workbench for classical guitar. The current version is a safe recovery and continued-development edition of an archived project, focused on local score + audio playback and synchronization.

## 当前版本能做什么 / What works now

- 本地曲库扫描，以及导入音频和谱面图片。
- 删除曲库中的曲目（带二次确认，仅删除 `songs/` 目录内对应曲目文件夹）。
- 播放 WAV、MP3、FLAC、OGG、M4A 等音频格式。
- 显示音频波形、时间刻度、播放进度和横向缩放（1×–20×）。
- 点击波形定位音频；按空格键播放/暂停。
- 自动识别常见单页谱面的谱行，区分独立五线谱与“五线谱 + 六线 TAB”系统。
- 播放光标同时显示在波形和谱面上，并在跨行时自动滚动到当前谱行。
- 非标记模式下点击谱面定位播放：有配对刻度时按真实轨迹反算，没有刻度时按谱行顺序和行内位置估算。
- 手动添加、任意位置插入、选中、删除和清空音频/谱面配对刻度。
- 中英双语界面，可即时切换并保存语言选择。
- 回归测试覆盖分行识别、左右边界、跨行轨迹、双语界面、空格快捷键和谱面点击跳播。

The current build supports local library scanning, audio/score import, safe song-folder deletion with confirmation, waveform and progress display, 1×–20× zoom, waveform seeking, Space-bar play/pause, automatic row detection, synchronized cursors, score clicking to seek, paired marker editing, bilingual UI, and regression tests.

## 已验证的曲目 / Verified sample scores

- 《绿袖子 / Greensleeves》：4 组“五线谱 + TAB”，已有配对刻度。
- 阿瓜多《Op.3 No.3》：5 行独立五线谱，含同版 MIDI 渲染音频。
- 卡尔卡西《Etude 1, Op.60 No.1》：密集单页谱面，含同版 MIDI 渲染音频。
- 《爱的罗曼史 / Spanish Romance》：7 行独立五线谱，含同版 MIDI 渲染音频。

The bundled scores and audio sources are recorded in each song's `info.json`.

## 运行 / Run

当前主要面向 Windows + Anaconda/Python 3.11：

```powershell
\anaconda3\python.exe main_window.py
```

依赖：PyQt6、numpy、opencv-python、librosa、sounddevice、soundfile。音频输出需要可用的系统音频设备。




## 优点 / Strengths

1. **本地闭环 / Self-contained local workflow**：曲库、谱面、波形、跳播和光标都在一个轻量桌面程序中完成，不依赖在线账户或云端服务。  
   The music library, scores, waveforms, seeking, and playback cursors are all handled within one lightweight desktop application, without requiring an online account or cloud service.

2. **版面结构识别 / Score layout recognition**：利用长横谱线、线距以及五线谱/TAB 结构，而不是只按固定垂直距离切图。  
   The system uses long horizontal staff lines, line spacing, and staff/TAB structure instead of relying solely on fixed vertical image slicing.

3. **自动与手动并存 / Automatic and manual workflows**：自动识别适合快速开始，配对刻度适合精确校准，并允许按音频时间任意插入。  
   Automatic recognition provides a quick starting point, while paired markers allow precise calibration and can be inserted at any audio position.

4. **适合继续开发 / Easy to continue developing**：代码集中、曲目采用文件夹 + `info.json`、测试可直接运行，贡献者容易上手。  
   The codebase is centralized, songs use a folder-plus-`info.json` structure, and the tests can be run directly, making it relatively easy for contributors to get started.

5. **交互已可用 / Usable interaction**：双语切换、空格播放/暂停、谱面点击跳播等功能适合实际练习。  
   Bilingual interface switching, Space-bar play/pause, and score-click seeking are already available for practical practice sessions.

6. **曲库管理直接 / Straightforward library management**：删除操作有确认、限定在曲库目录内，并会自动切换到剩余曲目。  
   Song deletion requires confirmation, is restricted to folders inside the library directory, and automatically switches to another available song.

## 缺点、限制与风险 / Limitations and Risks

1. **不是完整原版产品 / Not a complete reproduction of the original product**：OMR 音符级识别、录音评分、AI 教练、练习计划、在线搜索下载等功能尚未完整恢复，部分入口仍是占位提示。  
   Note-level OMR recognition, recording evaluation, AI coaching, practice plans, and online search/download features have not yet been fully restored. Some interface entries remain placeholders.

2. **自动分行不是音乐语义识别 / Automatic line detection is not music-semantic recognition**：不理解拍号、反复记号、跳房子、复杂多声部或跨页关系。扫描件、倾斜图片、断线谱、双栏谱和异常排版可能需要人工校准。  
   The system does not understand time signatures, repeat signs, navigation symbols, complex polyphony, or cross-page relationships. Scanned pages, skewed images, broken staff lines, two-column layouts, and unusual formatting may require manual calibration.

3. **无刻度跳播只是估算 / Seeking without markers is only an estimate**：没有配对刻度时按行序和横向比例推算；可靠的逐小节同步仍需手动添加刻度。  
   When no paired markers are available, playback position is estimated from the line order and horizontal position. Reliable measure-by-measure synchronization still requires manually added markers.

4. **部分音频是合成音 / Some audio is synthesized**：根据同版 MIDI 本地渲染的 WAV 主要用于同步测试，不应宣传为正式真人演奏录音。  
   WAV files rendered locally from corresponding MIDI files are primarily intended for synchronization testing and should not be presented as official live or studio recordings.

5. **平台耦合 / Platform dependence**：当前启动说明、字体和音频输出主要按 Windows 配置编写；其他系统和音频驱动可能需要适配。  
   The current launch instructions, font assumptions, and audio output configuration are primarily designed for Windows. Other operating systems and audio drivers may require adaptation.

6. **许可证需要发布者选定 / The publisher must choose a license**：目录中同时提供 `LICENSE-MIT.txt` 与 `LICENSE-APACHE.txt` 两个正式许可证模板，二选一用于原创代码；第三方谱面、音频、MIDI 和字体需要逐项核查，`info.json` 不能替代完整版权审查。  
   The directory includes both `LICENSE-MIT.txt` and `LICENSE-APACHE.txt` as formal license templates. One should be selected for the original source code. Third-party scores, audio, MIDI files, and fonts must be reviewed individually, and `info.json` does not replace a complete copyright review.

7. **缺少发布工程 / Limited release engineering**：尚未提供稳定安装包、自动更新、跨平台构建或持续集成流水线。  
   A stable installer, automatic update mechanism, cross-platform build process, and continuous integration pipeline have not yet been provided.

8. **删除不可撤销 / Deletion cannot be undone**：曲目删除目前是直接移除整个曲目文件夹，没有回收站或恢复历史；发布前应考虑备份、软删除或撤销机制。  
   Deleting a song directly removes its entire song folder. There is no recycle bin or recovery history, so backups, soft deletion, or an undo mechanism should be considered before publication.



## 项目定位 / Project status

**本地吉他谱面与音频同步练习工作台（开发中）**。

**an in-development local guitar score and audio synchronization practice workbench**.
