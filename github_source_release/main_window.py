import json
import os
import sys
import threading
from bisect import bisect_right
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import cv2
import numpy as np
import sounddevice as sd
import soundfile as sf

from PyQt6.QtCore import QObject, QSettings, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QColor, QFont, QKeySequence, QPainter, QPainterPath, QPen, QPixmap, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


APP_DIR = Path(__file__).resolve().parent
SONGS_DIR = APP_DIR / "songs"
SUPPORTED_AUDIO = {".mp3", ".wav", ".flac", ".ogg", ".m4a"}
SUPPORTED_IMAGE = {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}


TRANSLATIONS = {
    "zh": {
        "window_title": "吉他学习助手",
        "file": "文件",
        "language": "Language",
        "chinese": "中文",
        "english": "English",
        "import_local": "导入本地音频/谱面",
        "rescan": "重新扫描曲库",
        "library": "我的曲库",
        "import_song": "导入曲目",
        "delete_song": "删除曲目",
        "delete_song_title": "删除曲目",
        "delete_song_question": "确定删除“{title}”及其音频、谱面和刻度数据吗？此操作不可撤销。",
        "delete_song_missing": "请先在曲库中选择要删除的曲目。",
        "delete_song_failed": "删除曲目失败",
        "choose_song": "请选择或导入一首曲目",
        "play_demo": "播放示范",
        "pause": "暂停",
        "waveform_zoom": "波形横向缩放",
        "reset_zoom": "恢复 1×",
        "add_marker": "添加配对刻度",
        "exit_marker": "退出标记模式",
        "delete_last": "删除最后一组",
        "delete_selected": "删除选中刻度",
        "clear_markers": "清空全部刻度",
        "marker_disabled": "刻度模式：未启用",
        "score_tab": "谱面与分段",
        "practice_tab": "跟练",
        "recovery_tab": "恢复状态",
        "target_bpm": "目标 BPM",
        "listen_demo": "先听示范",
        "practice_phrase": "开始练这一句",
        "record_score": "录音并评分",
        "ai_advice": "生成 AI 教练建议",
        "practice_hint": "归档记录表明原版支持 OMR 分段、跟弹评分、AI 教练和阶段练习计划。\n当前恢复版先提供可启动的练习工作台，完整算法模块仍待从增量补丁继续还原。",
        "recovery_text": "已从 Codex 归档确认的功能：\n• 曲库与文件导入\n• 音频播放和录音\n• 音频/谱面分段与 OMR\n• 谱面高亮和跟弹评分\n• AI 教练建议\n• 练习计划与阶段管理\n• YouTube 搜索下载及 Cookies 支持\n\n恢复说明：原临时目录中的 .py/.pyc/.exe 已全部消失；这里是可运行的安全恢复外壳，不冒充完整原版。",
        "started": "程序已启动",
        "library_count": "曲库扫描完成，共 {count} 首",
        "loaded": "已载入：{title}",
        "select_audio": "选择音频",
        "select_score": "选择谱面（可跳过）",
        "audio_filter": "音频 (*.mp3 *.wav *.flac *.ogg *.m4a);;所有文件 (*)",
        "image_filter": "图片 (*.png *.jpg *.jpeg *.bmp *.tiff)",
        "audio_load_failed": "音频载入失败",
        "notice": "提示",
        "choose_audio_song": "请先选择含音频的曲目。",
        "archived_unavailable": "这个入口已恢复，但对应的最新算法源码仍在归档增量中，当前未启用。",
        "selected_marker": "已选中 S{index}（{time}），可点击删除或按 Delete",
        "removed_marker": "已删除刻度（{time}），剩余 {count} 组",
        "cannot_add": "无法添加",
        "need_audio_score": "必须先选择同时包含音频和谱面的曲目。",
        "marker_step1": "第 1 步：请在上方音频波形点击时间位置",
        "normal_mode": "普通播放定位模式。已保存 {count} 组配对刻度",
        "marker_step2": "第 2 步：音频已定在 {time}，请在谱面对应位置点击添加纵向刻度",
        "select_audio_first": "先选音频",
        "select_audio_position": "请先在音频波形上点击对应的时间位置。",
        "outside_row": "不在谱行内",
        "click_row": "请点击自动识别出的虚线谱行框内部。",
        "inserted_marker": "已插入 S{index}，全部刻度已按音频时间重新编号。可继续在任意位置添加",
        "paired_count": "严格配对刻度：{count} 组",
        "clear_title": "清空刻度",
        "clear_question": "确定删除当前曲目的全部音频/谱面配对刻度吗？",
        "play_failed": "播放失败",
        "audio_device_failed": "无法打开音频设备：\n{message}",
        "waveform_empty": "选择曲目后显示音频波形",
        "pending": "待配对",
        "selected": "选中",
        "score_empty": "该曲目暂无谱面",
        "choose_score": "请选择谱面",
        "row": "第{index}行",
        "playing": "播放",
    },
    "en": {
        "window_title": "Guitar Learning Assistant",
        "file": "File",
        "language": "语言",
        "chinese": "中文",
        "english": "English",
        "import_local": "Import Local Audio / Score",
        "rescan": "Rescan Library",
        "library": "My Library",
        "import_song": "Import Song",
        "delete_song": "Delete Song",
        "delete_song_title": "Delete Song",
        "delete_song_question": "Delete “{title}” and all of its audio, scores, and marker data? This cannot be undone.",
        "delete_song_missing": "Select a song to delete first.",
        "delete_song_failed": "Delete Song Failed",
        "choose_song": "Choose or import a song",
        "play_demo": "Play Demo",
        "pause": "Pause",
        "waveform_zoom": "Waveform Horizontal Zoom",
        "reset_zoom": "Reset to 1×",
        "add_marker": "Add Paired Marker",
        "exit_marker": "Exit Marker Mode",
        "delete_last": "Delete Last Pair",
        "delete_selected": "Delete Selected Marker",
        "clear_markers": "Clear All Markers",
        "marker_disabled": "Marker mode: off",
        "score_tab": "Score & Segments",
        "practice_tab": "Practice",
        "recovery_tab": "Recovery Status",
        "target_bpm": "Target BPM",
        "listen_demo": "Listen to Demo",
        "practice_phrase": "Practice This Phrase",
        "record_score": "Record & Score",
        "ai_advice": "Generate AI Coach Advice",
        "practice_hint": "Archived records indicate that the original app supported OMR segmentation, play-along scoring, AI coaching, and staged practice plans.\nThis recovered edition currently provides a working practice desk while the remaining algorithm modules await restoration from incremental patches.",
        "recovery_text": "Features confirmed from the Codex archive:\n• Library and file import\n• Audio playback and recording\n• Audio/score segmentation and OMR\n• Score highlighting and play-along assessment\n• AI coaching advice\n• Practice plans and stage management\n• YouTube search/download and cookie support\n\nRecovery note: the original temporary .py/.pyc/.exe files are gone. This is a safe, runnable recovery shell and does not claim to be the complete original version.",
        "started": "Application started",
        "library_count": "Library scan complete: {count} songs",
        "loaded": "Loaded: {title}",
        "select_audio": "Select Audio",
        "select_score": "Select Score (optional)",
        "audio_filter": "Audio (*.mp3 *.wav *.flac *.ogg *.m4a);;All Files (*)",
        "image_filter": "Images (*.png *.jpg *.jpeg *.bmp *.tiff)",
        "audio_load_failed": "Audio Load Failed",
        "notice": "Notice",
        "choose_audio_song": "Please select a song containing audio first.",
        "archived_unavailable": "This entry point has been restored, but its latest algorithm source is still in archived increments and is not enabled yet.",
        "selected_marker": "Selected S{index} ({time}); click Delete or press the Delete key",
        "removed_marker": "Deleted marker ({time}); {count} pairs remain",
        "cannot_add": "Cannot Add",
        "need_audio_score": "Select a song containing both audio and a score first.",
        "marker_step1": "Step 1: click a time position in the waveform above",
        "normal_mode": "Normal playback positioning. {count} paired markers saved",
        "marker_step2": "Step 2: audio is set to {time}; click the matching score position to add a vertical marker",
        "select_audio_first": "Select Audio First",
        "select_audio_position": "Click the corresponding time position in the waveform first.",
        "outside_row": "Outside a Score Row",
        "click_row": "Click inside one of the automatically detected dashed score-row boxes.",
        "inserted_marker": "Inserted S{index}; all markers were renumbered by audio time. You can continue adding anywhere",
        "paired_count": "Strict paired markers: {count}",
        "clear_title": "Clear Markers",
        "clear_question": "Delete all paired audio/score markers for the current song?",
        "play_failed": "Playback Failed",
        "audio_device_failed": "Unable to open the audio device:\n{message}",
        "waveform_empty": "Select a song to display its waveform",
        "pending": "Pending pair",
        "selected": "Selected",
        "score_empty": "No score is available for this song",
        "choose_score": "Select a score",
        "row": "Row {index}",
        "playing": "Playing",
    },
}


class AudioEngine(QObject):
    state_changed = pyqtSignal(bool)
    error = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.samples = np.zeros((0, 2), dtype=np.float32)
        self.sample_rate = 44100
        self.position_frames = 0
        self.stream = None
        self.playing = False
        self.lock = threading.Lock()

    @property
    def duration_ms(self):
        return int(len(self.samples) * 1000 / self.sample_rate) if self.sample_rate else 0

    @property
    def position_ms(self):
        with self.lock:
            return int(self.position_frames * 1000 / self.sample_rate) if self.sample_rate else 0

    def load(self, path):
        self.stop(reset=True)
        # Keep the source sample rate. The audio cursor already uses the same
        # frame clock, so score synchronization must not alter this path.
        audio, rate = sf.read(str(path), dtype="float32", always_2d=False)
        audio = np.asarray(audio, dtype=np.float32)
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)
        peak = float(np.max(np.abs(audio))) if audio.size else 0.0
        if peak > 1.0:
            audio = audio / peak
        self.samples = np.column_stack((audio, audio)).astype(np.float32, copy=False)
        self.sample_rate = int(rate)
        self.position_frames = 0
        return audio

    def play(self):
        if not len(self.samples):
            return
        if self.position_frames >= len(self.samples):
            self.position_frames = 0
        try:
            self.stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=2,
                dtype="float32",
                callback=self._callback,
                finished_callback=self._finished,
                blocksize=1024,
                latency="low",
            )
            self.stream.start()
            self.playing = True
            self.state_changed.emit(True)
        except Exception as exc:
            self.playing = False
            self.error.emit(str(exc))

    def pause(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.playing = False
        self.state_changed.emit(False)

    def stop(self, reset=False):
        self.pause()
        if reset:
            with self.lock:
                self.position_frames = 0

    def seek_ms(self, value):
        with self.lock:
            self.position_frames = max(0, min(len(self.samples), int(value * self.sample_rate / 1000)))

    def _callback(self, outdata, frames, _time, _status):
        with self.lock:
            start = self.position_frames
            end = min(start + frames, len(self.samples))
            count = end - start
            outdata.fill(0)
            if count:
                outdata[:count] = self.samples[start:end]
            self.position_frames = end
        if count < frames:
            raise sd.CallbackStop()

    def _finished(self):
        self.playing = False
        self.state_changed.emit(False)


class WaveformWidget(QWidget):
    seek_requested = pyqtSignal(float)
    marker_requested = pyqtSignal(float)
    marker_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.waveform = np.zeros(0, dtype=np.float32)
        self.progress = 0.0
        self.duration_ms = 0
        self.markers = []
        self.pending_marker_ms = None
        self.marker_mode = False
        self.selected_marker_index = -1
        self._wave_path_cache = None
        self._wave_path_width = 0
        self.language = "zh"
        self.setFixedHeight(132)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_audio(self, samples, duration_ms=0):
        samples = np.asarray(samples, dtype=np.float32)
        target_points = 1200
        if samples.size > target_points:
            block = max(1, samples.size // target_points)
            trimmed = samples[: samples.size - samples.size % block]
            self.waveform = np.max(np.abs(trimmed.reshape(-1, block)), axis=1)
        else:
            self.waveform = np.abs(samples)
        peak = float(np.max(self.waveform)) if self.waveform.size else 0.0
        if peak:
            self.waveform /= peak
        self.duration_ms = int(duration_ms)
        self.progress = 0.0
        self._wave_path_cache = None
        self._wave_path_width = 0
        self.update()

    def set_progress(self, ratio):
        self.progress = max(0.0, min(1.0, float(ratio)))
        self.update()

    def resizeEvent(self, event):
        self._wave_path_cache = None
        self._wave_path_width = 0
        super().resizeEvent(event)

    def set_markers(self, markers):
        self.markers = list(markers)
        if self.selected_marker_index >= len(self.markers):
            self.selected_marker_index = -1
        self.update()

    def set_selected_marker(self, index):
        self.selected_marker_index = int(index) if index is not None else -1
        self.update()

    def set_pending_marker(self, marker_ms):
        self.pending_marker_ms = marker_ms
        self.update()

    def set_marker_mode(self, enabled):
        self.marker_mode = bool(enabled)
        self.setCursor(Qt.CursorShape.CrossCursor if enabled else Qt.CursorShape.PointingHandCursor)

    def set_language(self, language):
        self.language = language if language in TRANSLATIONS else "zh"
        self.update()

    def _tr(self, key, **values):
        return TRANSLATIONS[self.language][key].format(**values)

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#20221d"))
        if not self.waveform.size:
            painter.setPen(QColor("#8f9484"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._tr("waveform_empty"))
            return
        width = max(1, self.width())
        height = self.height()
        ruler_height = 26
        middle = ruler_height + (height - ruler_height) / 2
        painter.setPen(QPen(QColor("#4b5044"), 1))
        painter.drawLine(0, ruler_height, width, ruler_height)
        if self.duration_ms:
            duration_seconds = self.duration_ms / 1000
            target_interval = max(0.1, duration_seconds / max(1, width / 100))
            nice_steps = (0.1, 0.2, 0.5, 1, 2, 5, 10, 15, 30, 60, 120, 300)
            interval = next((step for step in nice_steps if step >= target_interval), nice_steps[-1])
            tick = 0.0
            painter.setPen(QColor("#a8ad9f"))
            while tick <= duration_seconds + 1e-6:
                x = int(tick / duration_seconds * width)
                painter.drawLine(x, 15, x, ruler_height)
                minutes = int(tick) // 60
                seconds = int(tick) % 60
                painter.drawText(x + 3, 13, f"{minutes:02d}:{seconds:02d}")
                tick += interval
        if self._wave_path_cache is None or self._wave_path_width != width:
            path = QPainterPath()
            for x in range(width):
                index = min(len(self.waveform) - 1, int(x * len(self.waveform) / width))
                amplitude = float(self.waveform[index]) * ((height - ruler_height) * 0.40)
                path.moveTo(x, middle - amplitude)
                path.lineTo(x, middle + amplitude)
            self._wave_path_cache = path
            self._wave_path_width = width
        path = self._wave_path_cache
        painter.setPen(QPen(QColor("#657052"), 1.2))
        painter.drawPath(path)
        played_width = int(width * self.progress)
        if played_width:
            painter.save()
            painter.setClipRect(0, 0, played_width, height)
            painter.setPen(QPen(QColor("#e0a35a"), 1.6))
            painter.drawPath(path)
            painter.restore()
        painter.setPen(QPen(QColor("#fff0d7"), 2))
        painter.drawLine(played_width, ruler_height, played_width, height - 8)
        painter.setFont(QFont("Microsoft YaHei UI", 9, QFont.Weight.Bold))
        for index, marker_ms in enumerate(self.markers, 1):
            x = int(width * marker_ms / self.duration_ms) if self.duration_ms else 0
            selected = index - 1 == self.selected_marker_index
            painter.setPen(QPen(QColor("#ffe06a") if selected else QColor("#63d3c4"), 4 if selected else 2))
            painter.drawLine(x, ruler_height, x, height)
            painter.setPen(QColor("#fff5b0") if selected else QColor("#bff7ed"))
            suffix = f" {self._tr('selected')}" if selected else ""
            painter.drawText(x + 4, ruler_height + 15, f"S{index}{suffix}")
        if self.pending_marker_ms is not None and self.duration_ms:
            x = int(width * self.pending_marker_ms / self.duration_ms)
            painter.setPen(QPen(QColor("#ffd35a"), 2, Qt.PenStyle.DashLine))
            painter.drawLine(x, ruler_height, x, height)
            painter.setPen(QColor("#ffe9a5"))
            painter.drawText(x + 4, height - 8, self._tr("pending"))

    def mousePressEvent(self, event):
        self._seek(event.position().x())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._seek(event.position().x())

    def _seek(self, x):
        ratio = max(0.0, min(1.0, x / max(1, self.width())))
        if self.duration_ms and self.markers:
            marker_xs = [self.width() * marker_ms / self.duration_ms for marker_ms in self.markers]
            nearest = min(range(len(marker_xs)), key=lambda i: abs(marker_xs[i] - x))
            if abs(marker_xs[nearest] - x) <= 10:
                self.marker_selected.emit(nearest)
                return
        if self.marker_mode:
            self.marker_requested.emit(ratio)
        else:
            self.seek_requested.emit(ratio)


class ScoreWidget(QWidget):
    marker_requested = pyqtSignal(float, float)
    marker_selected = pyqtSignal(int)
    score_seek_requested = pyqtSignal(int, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.source_pixmap = QPixmap()
        self.row_boxes = []
        self.row_content_boxes = []
        self.markers = []
        self.marker_mode = False
        self.playback_position_ms = None
        self.playback_duration_ms = 0
        self.playback_markers = []
        self.playback_tracks = []
        self._playback_marker_signature = None
        self.selected_marker_index = -1
        self.language = "zh"
        self.setMinimumSize(600, 480)
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def set_score(self, image_path, confirmed_rows=None):
        self.source_pixmap = QPixmap(str(image_path))
        # A previously reviewed layout is authoritative. Automatic detection
        # remains the fallback for a new score or invalid saved metadata.
        self.row_boxes = self._normalize_confirmed_rows(confirmed_rows)
        if not self.row_boxes:
            self.row_boxes = self._detect_rows(str(image_path))
        self.row_content_boxes = self._detect_row_content_bounds(str(image_path), self.row_boxes)
        self.markers = []
        self.playback_position_ms = None
        self.playback_markers = []
        self.playback_tracks = []
        self._playback_marker_signature = None
        self._resize_to_width()
        self.update()

    def clear_score(self, text=None):
        self.source_pixmap = QPixmap()
        self.row_boxes = []
        self.row_content_boxes = []
        self.markers = []
        self.playback_position_ms = None
        self.playback_markers = []
        self._playback_marker_signature = None
        self.empty_text = text or self._tr("score_empty")
        self.setMinimumSize(600, 480)
        self.update()

    def set_language(self, language):
        self.language = language if language in TRANSLATIONS else "zh"
        self.update()

    def _tr(self, key, **values):
        return TRANSLATIONS[self.language][key].format(**values)

    def set_markers(self, markers):
        self.markers = list(markers)
        if self.selected_marker_index >= len(self.markers):
            self.selected_marker_index = -1
        self.update()

    def set_selected_marker(self, index):
        self.selected_marker_index = int(index) if index is not None else -1
        self.update()

    def set_playback_position(self, position_ms, duration_ms, paired_markers):
        """Update the score cursor using the same audio time base as the waveform."""
        self.playback_position_ms = int(position_ms) if duration_ms else None
        self.playback_duration_ms = int(duration_ms or 0)
        signature = tuple(
            (int(marker.get("time_ms", 0)), int(marker.get("row_index", -1)), round(float(marker.get("score_x", 0.0)), 6))
            for marker in (paired_markers or [])
            if "time_ms" in marker and "score_x" in marker
        )
        if signature != self._playback_marker_signature:
            self.playback_markers = sorted(
                [dict(marker) for marker in (paired_markers or []) if "time_ms" in marker and "score_x" in marker],
                key=lambda marker: int(marker["time_ms"]),
            )
            self._add_final_row_anchors()
            self._build_playback_tracks()
            self._playback_marker_signature = signature
        self.update()

    def _build_playback_tracks(self):
        """Build non-overlapping time tracks, including multi-row jumps."""
        marks = sorted(self.playback_markers, key=lambda marker: int(marker["time_ms"]))
        self.playback_tracks = []
        for first, second in zip(marks, marks[1:]):
            t1, t2 = int(first["time_ms"]), int(second["time_ms"])
            if t2 <= t1:
                continue
            row1 = int(first.get("row_index", 0)); row2 = int(second.get("row_index", row1))
            x1 = float(first["score_x"]); x2 = float(second["score_x"])
            if row2 == row1:
                self.playback_tracks.append((t1, t2, row1, x1, x2))
                continue
            if row2 > row1:
                # Follow the actual reading path: finish the source row, cross
                # every complete intermediate row, then reach the target mark.
                pieces = []
                _, source_right = self._row_content_bounds(row1)
                if source_right - x1 > 0.001:
                    pieces.append((row1, x1, source_right, source_right - x1))
                for row in range(row1 + 1, row2):
                    left, right = self._row_content_bounds(row)
                    pieces.append((row, left, right, max(0.001, right - left)))
                target_left, _ = self._row_content_bounds(row2)
                if x2 - target_left > 0.001:
                    pieces.append((row2, target_left, x2, x2 - target_left))
                if not pieces:
                    pieces.append((row2, target_left, x2, 1.0))
                total_weight = sum(piece[3] for piece in pieces)
                elapsed_weight = 0.0
                for row, start_x, end_x, weight in pieces:
                    start_t = t1 + int(round((t2 - t1) * elapsed_weight / total_weight))
                    elapsed_weight += weight
                    end_t = t1 + int(round((t2 - t1) * elapsed_weight / total_weight))
                    self.playback_tracks.append((start_t, max(start_t + 1, end_t), row, start_x, end_x))
                continue
            # Backward/nonlinear row edits are uncommon; retain direct
            # interpolation so manually reordered marks remain usable.
            self.playback_tracks.append((t1, t2, row1, x1, x2))

    def _add_final_row_anchors(self):
        """Add only missing anchors after the last real mark.

        Cross-row intervals are handled directly by ``_playback_cursor``. We
        intentionally do not insert duplicate same-time anchors at row
        boundaries: duplicate timestamps make the active row ambiguous.
        """
        if not self.playback_markers or not self.row_boxes:
            return
        previous = self.playback_markers[-1]
        previous_row = int(previous.get("row_index", 0))
        missing_rows = len(self.row_boxes) - 1 - previous_row
        if self.playback_duration_ms <= int(previous["time_ms"]):
            return
        span = self.playback_duration_ms - int(previous["time_ms"])
        # Reserve the last slice for motion across the final row, so a
        # synthetic row-start is not placed at the exact audio end.
        if missing_rows > 0:
            slices = missing_rows + 1
            for offset in range(1, missing_rows + 1):
                next_row = previous_row + offset
                next_time = int(previous["time_ms"]) + int(round(span * offset / slices))
                left, _ = self._row_content_bounds(next_row)
                self.playback_markers.append(
                    {"time_ms": next_time, "row_index": next_row, "score_x": left, "_inferred": True}
                )
        _, right = self._row_content_bounds(len(self.row_boxes) - 1)
        if int(self.playback_markers[-1]["time_ms"]) < self.playback_duration_ms:
            self.playback_markers.append(
                {"time_ms": int(self.playback_duration_ms), "row_index": len(self.row_boxes) - 1, "score_x": right, "_inferred": True}
            )

    def set_marker_mode(self, enabled):
        self.marker_mode = bool(enabled)
        self.setCursor(Qt.CursorShape.CrossCursor if enabled else Qt.CursorShape.ArrowCursor)

    def _resize_to_width(self):
        if self.source_pixmap.isNull():
            return
        width = max(820, self.parentWidget().width() if self.parentWidget() else 820)
        height = int(width * self.source_pixmap.height() / self.source_pixmap.width())
        self.setFixedSize(width, height)

    @staticmethod
    def _normalize_confirmed_rows(rows):
        """Validate normalized row boxes loaded from a song's metadata."""
        normalized = []
        try:
            for row in rows or []:
                if isinstance(row, dict):
                    top, bottom = float(row["top"]), float(row["bottom"])
                else:
                    top, bottom = float(row[0]), float(row[1])
                if not (0.0 <= top < bottom <= 1.0):
                    return []
                if normalized and top < normalized[-1][1]:
                    return []
                normalized.append((top, bottom))
        except (KeyError, TypeError, ValueError, IndexError):
            return []
        return normalized

    @staticmethod
    def _detect_rows(path):
        image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            return []
        height, width = image.shape
        inverse = cv2.threshold(image, 205, 255, cv2.THRESH_BINARY_INV)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(80, width // 8), 1))
        horizontal = cv2.morphologyEx(inverse, cv2.MORPH_OPEN, kernel)
        density = (horizontal > 0).sum(axis=1)
        line_ys = np.where(density > width * 0.35)[0]
        groups = []
        for y in line_ys:
            if not groups or y - groups[-1][-1] > 5:
                groups.append([int(y)])
            else:
                groups[-1].append(int(y))
        centers = [int((group[0] + group[-1]) / 2) for group in groups]
        # Split the detected long lines by their local spacing. Staff-internal
        # gaps are small and consistent; gaps between staves/systems are much
        # larger. A scale-relative rule works for dense and sparse engraving
        # without relying on a fixed page-resolution threshold.
        clusters = []
        index = 0
        while index < len(centers):
            cluster = [centers[index]]
            index += 1
            while index < len(centers):
                recent_gaps = np.diff(cluster[-4:])
                expected_gap = float(np.median(recent_gaps)) if recent_gaps.size else None
                gap = centers[index] - cluster[-1]
                if expected_gap is not None and gap > max(30.0, expected_gap * 2.2):
                    break
                if expected_gap is None and gap > 30:
                    break
                cluster.append(centers[index])
                index += 1
            clusters.append(cluster)

        # Preserve the semantic difference between a five-line standard staff
        # and a six-line guitar tablature staff.  Greensleeves uses 5+6 pairs;
        # a standard-notation-only score such as Aguado is 5+5+5... and must
        # never be merged merely because adjacent systems are close together.
        staves = [cluster for cluster in clusters if len(cluster) in (5, 6)]
        rows = []
        index = 0
        while index < len(staves):
            staff = staves[index]
            top = max(0, staff[0] - 55)
            bottom = min(height, staff[-1] + 25)
            if len(staff) == 5 and index + 1 < len(staves) and len(staves[index + 1]) == 6:
                tablature = staves[index + 1]
                staff_spacing = float(np.median(np.diff(staff)))
                tab_spacing = float(np.median(np.diff(tablature)))
                inter_staff_gap = tablature[0] - staff[-1]
                # A plausible standard+TAB system has a clear but bounded gap.
                # This rejects unrelated footer lines and unusually distant
                # six-line material while retaining common guitar layouts.
                if max(staff_spacing, tab_spacing) * 2 <= inter_staff_gap <= max(staff_spacing, tab_spacing) * 10:
                    bottom = min(height, tablature[-1] + 25)
                    index += 1
            rows.append((top / height, bottom / height))
            index += 1
        return rows

    @staticmethod
    def _detect_row_content_bounds(path, rows):
        """Find the horizontal ink bounds for each detected music row.

        Staff lines are much more reliable page-layout evidence than vertical
        ink: stems and barlines can occur anywhere in a system and must not be
        mistaken for its left edge.  Find the common endpoints of the long
        horizontal staff lines, then skip a scale-aware clef/key/time header.
        """
        image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            return [(0.03, 0.97) for _ in rows]
        height, width = image.shape
        bounds = []
        for top, bottom in rows:
            y1, y2 = max(0, int(top * height)), min(height, int(bottom * height))
            roi = image[y1:y2]
            projection = (roi < 200).sum(axis=0)
            columns = np.where(projection > 2)[0]
            inverse = cv2.threshold(roi, 205, 255, cv2.THRESH_BINARY_INV)[1]
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(80, width // 8), 1))
            horizontal = cv2.morphologyEx(inverse, cv2.MORPH_OPEN, kernel)
            line_density = (horizontal > 0).sum(axis=1)
            line_ys = np.where(line_density > width * 0.35)[0]
            line_groups = []
            for y in line_ys:
                if not line_groups or y - line_groups[-1][-1] > 5:
                    line_groups.append([int(y)])
                else:
                    line_groups[-1].append(int(y))
            line_centers = [int((group[0] + group[-1]) / 2) for group in line_groups]
            line_extents = []
            for center in line_centers:
                pixels = np.where(horizontal[center] > 0)[0]
                if pixels.size:
                    line_extents.append((int(pixels[0]), int(pixels[-1])))

            if columns.size and len(line_extents) >= 5:
                staff_left = int(round(float(np.median([extent[0] for extent in line_extents]))))
                staff_right = int(round(float(np.median([extent[1] for extent in line_extents]))))
                spacings = np.diff(line_centers)
                # The first five long lines are the standard staff in both a
                # notation-only system and a notation+TAB system. Use its four
                # internal gaps as the symbol scale; TAB is often printed with
                # wider spacing and would otherwise push the start too far.
                standard_staff_spacings = spacings[:4] if spacings.size >= 4 else spacings
                staff_spacing = float(np.median(standard_staff_spacings)) if standard_staff_spacings.size else max(7.0, width / 120.0)
                header_width = max(36, int(round(staff_spacing * 5.25)))
                left = min(width - 1, staff_left + header_width)
                right = min(width - 1, staff_right + 4)
                if left >= right:
                    left = max(0, int(columns[0]))
                bounds.append((left / width, right / width))
            else:
                # Conservative fallback for scans whose staff lines are too
                # broken for morphology; unlike the old path, it never treats
                # an arbitrary tall note stem as a page boundary.
                left = int(columns[0]) if columns.size else int(width * 0.03)
                right = int(columns[-1]) + 4 if columns.size else int(width * 0.97)
                bounds.append((max(0, left) / width, min(width - 1, right) / width))
        return bounds

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#f5f3ea"))
        if self.source_pixmap.isNull():
            painter.setPen(QColor("#555"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, getattr(self, "empty_text", self._tr("choose_score")))
            return
        painter.drawPixmap(self.rect(), self.source_pixmap)
        painter.setFont(QFont("Microsoft YaHei UI", 10, QFont.Weight.Bold))
        for row_index, (top, bottom) in enumerate(self.row_boxes, 1):
            y1, y2 = int(top * self.height()), int(bottom * self.height())
            painter.setPen(QPen(QColor(55, 150, 135, 170), 2, Qt.PenStyle.DashLine))
            painter.drawRect(2, y1, self.width() - 5, max(1, y2 - y1))
            painter.fillRect(4, y1 + 3, 48, 20, QColor(26, 75, 68, 210))
            painter.setPen(QColor("#dffff8"))
            painter.drawText(9, y1 + 18, self._tr("row", index=row_index))
        for index, marker in enumerate(self.markers, 1):
            x = int(marker["x"] * self.width())
            y1 = int(marker["row_top"] * self.height())
            y2 = int(marker["row_bottom"] * self.height())
            selected = index - 1 == self.selected_marker_index
            painter.setPen(QPen(QColor("#ffe06a") if selected else QColor("#e05252"), 5 if selected else 3))
            painter.drawLine(x, y1, x, y2)
            painter.fillRect(x + 3, y1 + 2, 62 if selected else 34, 20, QColor(177, 38, 38, 220))
            painter.setPen(QColor("#fff5b0") if selected else QColor("white"))
            suffix = f" {self._tr('selected')}" if selected else ""
            painter.drawText(x + 7, y1 + 17, f"S{index}{suffix}")

        cursor = self._playback_cursor()
        if cursor is not None:
            row_index, x_ratio = cursor
            if 0 <= row_index < len(self.row_boxes):
                row_top, row_bottom = self.row_boxes[row_index]
                x = int(max(0.0, min(1.0, x_ratio)) * self.width())
                y1, y2 = int(row_top * self.height()), int(row_bottom * self.height())
                painter.setPen(QPen(QColor("#ffb347"), 3))
                painter.drawLine(x, y1, x, y2)
                painter.setBrush(QColor("#ffb347"))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(x - 5, max(2, y1 - 7), 10, 10)

    def _playback_cursor(self):
        """Return (row index, x ratio) for the current audio time.

        Between paired marks on the same score row, the cursor is linearly
        interpolated. At a row transition it travels to the end of the old
        row, then starts at the next mark, keeping audio and score visibly tied.
        """
        if self.playback_position_ms is None or not self.playback_markers or not self.row_boxes:
            return None
        if self.playback_tracks:
            time_ms = self.playback_position_ms
            for start_t, end_t, row, start_x, end_x in self.playback_tracks:
                if start_t <= time_ms < end_t:
                    amount = (time_ms - start_t) / max(1, end_t - start_t)
                    return row, self._clamp_row_x(row, start_x + (end_x - start_x) * amount)
            if time_ms >= self.playback_tracks[-1][1]:
                _, _, row, _, end_x = self.playback_tracks[-1]
                return row, self._clamp_row_x(row, end_x)
        marks = self.playback_markers
        time_ms = self.playback_position_ms
        # Playback anchors may be synthesized for unmarked rows. Keep only
        # one anchor per timestamp for interval construction; duplicate times
        # otherwise create zero-length intervals and hide the intended row.
        normalized = []
        for marker in marks:
            if normalized and int(marker["time_ms"]) == int(normalized[-1]["time_ms"]):
                continue
            normalized.append(marker)
        marks = normalized
        times = [int(marker["time_ms"]) for marker in marks]
        boundary_time = time_ms
        if time_ms < times[0]:
            first = marks[0]
            row = int(first.get("row_index", 0))
            return row, self._clamp_row_x(row, float(first["score_x"]))

        # Find the enclosing time interval, then map its progress across the
        # complete row span. This explicitly supports row jumps such as 0→2
        # or 0→3: each intermediate row receives an equal time slice.
        for first, second in zip(marks, marks[1:]):
            t1, t2 = int(first["time_ms"]), int(second["time_ms"])
            if t1 <= boundary_time < t2:
                row1 = int(first.get("row_index", 0))
                row2 = int(second.get("row_index", row1))
                x1 = float(first["score_x"])
                x2 = float(second["score_x"])
                progress = max(0.0, min(1.0, (time_ms - t1) / max(1, t2 - t1)))
                if row1 == row2:
                    return row1, self._clamp_row_x(row1, x1 + (x2 - x1) * progress)
                row_count = max(1, row2 - row1)
                row_position = min(row_count - 1, int(progress * row_count))
                row = row1 + row_position
                local = progress * row_count - row_position
                start_x = x1 if row == row1 else self._row_content_bounds(row)[0]
                end_x = x2 if row == row2 else self._row_content_bounds(row)[1]
                return row, self._clamp_row_x(row, start_x + (end_x - start_x) * local)

        last = marks[-1]
        last_row = int(last.get("row_index", 0))
        last_x = float(last["score_x"])
        tail = max(1, self.playback_duration_ms - int(last["time_ms"]))
        amount = max(0.0, min(1.0, (time_ms - int(last["time_ms"])) / tail))
        _, right = self._row_content_bounds(last_row)
        return last_row, self._clamp_row_x(last_row, last_x + (right - last_x) * amount)

    def _row_content_bounds(self, row_index):
        if 0 <= row_index < len(self.row_content_boxes):
            return self.row_content_boxes[row_index]
        return 0.03, 0.97

    def _clamp_row_x(self, row_index, x_ratio):
        left, right = self._row_content_bounds(row_index)
        return max(left, min(right, float(x_ratio)))

    def playback_row_index(self):
        cursor = self._playback_cursor()
        return cursor[0] if cursor is not None else None

    def score_position_to_time(self, row_index, x_ratio):
        """Map a clicked score position back to the audio timeline."""
        if not self.row_boxes:
            return None
        row_index = max(0, min(len(self.row_boxes) - 1, int(row_index)))
        left, right = self._row_content_bounds(row_index)
        x_ratio = max(left, min(right, float(x_ratio)))
        if self.playback_tracks:
            candidates = []
            for start_t, end_t, row, start_x, end_x in self.playback_tracks:
                if row != row_index:
                    continue
                lo, hi = sorted((float(start_x), float(end_x)))
                if lo - 1e-6 <= x_ratio <= hi + 1e-6 and abs(end_x - start_x) > 1e-6:
                    amount = (x_ratio - start_x) / (end_x - start_x)
                    candidates.append(start_t + amount * (end_t - start_t))
            if candidates:
                return int(round(min(candidates)))
            endpoints = []
            for start_t, end_t, row, start_x, end_x in self.playback_tracks:
                if row == row_index:
                    endpoints.extend(((abs(x_ratio - start_x), start_t), (abs(x_ratio - end_x), end_t)))
            if endpoints:
                return int(round(min(endpoints)[1]))
        row_progress = (x_ratio - left) / max(1e-6, right - left)
        return (row_index + row_progress) / max(1, len(self.row_boxes))

    def mousePressEvent(self, event):
        if self.source_pixmap.isNull():
            return
        x_ratio = max(0.0, min(1.0, event.position().x() / max(1, self.width())))
        y_ratio = max(0.0, min(1.0, event.position().y() / max(1, self.height())))
        for index, marker in enumerate(self.markers):
            marker_x = float(marker["x"])
            marker_top = float(marker["row_top"])
            marker_bottom = float(marker["row_bottom"])
            if abs(marker_x - x_ratio) * self.width() <= 12 and marker_top <= y_ratio <= marker_bottom:
                self.marker_selected.emit(index)
                return
        if not self.marker_mode:
            row_index = next(
                (index for index, (top, bottom) in enumerate(self.row_boxes) if top <= y_ratio <= bottom),
                None,
            )
            if row_index is not None:
                left, right = self._row_content_bounds(row_index)
                if left <= x_ratio <= right:
                    self.score_seek_requested.emit(row_index, x_ratio)
            return
        self.marker_requested.emit(x_ratio, y_ratio)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("Codex", "GuitarLearningAssistant")
        self.language = str(self.settings.value("language", "zh"))
        if self.language not in TRANSLATIONS:
            self.language = "zh"
        self.resize(1280, 820)
        self.songs = []
        self.current_song = None
        self.segment_markers = []
        self.selected_marker_index = -1
        self._last_auto_scroll_row = None
        self.pending_audio_marker_ms = None
        self.audio = AudioEngine(self)
        self.audio.state_changed.connect(self._on_state)
        self.audio.error.connect(self._audio_error)
        self.progress_timer = QTimer(self)
        self.progress_timer.setInterval(50)
        self.progress_timer.timeout.connect(self._refresh_progress)
        self.progress_timer.start()

        self._build_ui()
        self.play_pause_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        self.play_pause_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        self.play_pause_shortcut.setAutoRepeat(False)
        self.play_pause_shortcut.activated.connect(self.toggle_play)
        self._apply_theme()
        self.reload_library()
        self._apply_language()

    def _tr(self, key, **values):
        return TRANSLATIONS[self.language][key].format(**values)

    def _build_ui(self):
        self.file_menu = self.menuBar().addMenu("")
        self.import_action = QAction("", self)
        self.import_action.triggered.connect(self.import_song)
        self.file_menu.addAction(self.import_action)
        self.rescan_action = QAction("", self)
        self.rescan_action.triggered.connect(self.reload_library)
        self.file_menu.addAction(self.rescan_action)
        self.language_menu = self.menuBar().addMenu("")
        self.chinese_action = QAction("中文", self)
        self.chinese_action.triggered.connect(lambda: self._set_language("zh"))
        self.english_action = QAction("English", self)
        self.english_action.triggered.connect(lambda: self._set_language("en"))
        self.language_menu.addActions([self.chinese_action, self.english_action])

        root = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(root)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        self.library_title = QLabel()
        self.library_title.setObjectName("sectionTitle")
        left_layout.addWidget(self.library_title)
        self.song_list = QListWidget()
        self.song_list.currentRowChanged.connect(self.select_song)
        left_layout.addWidget(self.song_list, 1)
        self.import_btn = QPushButton()
        self.import_btn.clicked.connect(self.import_song)
        left_layout.addWidget(self.import_btn)
        self.delete_song_btn = QPushButton()
        self.delete_song_btn.setEnabled(False)
        self.delete_song_btn.clicked.connect(self.delete_current_song)
        left_layout.addWidget(self.delete_song_btn)
        root.addWidget(left)

        center = QWidget()
        center_layout = QVBoxLayout(center)
        self.song_title = QLabel()
        self.song_title.setObjectName("heroTitle")
        center_layout.addWidget(self.song_title)

        transport = QHBoxLayout()
        self.play_btn = QPushButton()
        self.play_btn.setObjectName("primaryButton")
        self.play_btn.clicked.connect(self.toggle_play)
        transport.addWidget(self.play_btn)
        self.time_label = QLabel("00:00 / 00:00")
        transport.addWidget(self.time_label)
        center_layout.addLayout(transport)

        zoom_row = QHBoxLayout()
        self.zoom_title = QLabel()
        zoom_row.addWidget(self.zoom_title)
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(1, 20)
        self.zoom_slider.setValue(1)
        self.zoom_slider.setPageStep(1)
        self.zoom_slider.valueChanged.connect(self._set_waveform_zoom)
        zoom_row.addWidget(self.zoom_slider, 1)
        self.zoom_label = QLabel("1×")
        self.zoom_label.setMinimumWidth(38)
        zoom_row.addWidget(self.zoom_label)
        self.reset_zoom_btn = QPushButton()
        self.reset_zoom_btn.clicked.connect(lambda: self.zoom_slider.setValue(1))
        zoom_row.addWidget(self.reset_zoom_btn)
        center_layout.addLayout(zoom_row)

        self.waveform = WaveformWidget()
        self.waveform.seek_requested.connect(self._seek_ratio)
        self.waveform.marker_requested.connect(self._set_pending_audio_marker)
        self.waveform.marker_selected.connect(self._select_marker)
        self.waveform_scroll = QScrollArea()
        self.waveform_scroll.setWidgetResizable(False)
        self.waveform_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.waveform_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.waveform_scroll.setFixedHeight(154)
        self.waveform_scroll.setWidget(self.waveform)
        center_layout.addWidget(self.waveform_scroll)

        segment_row = QHBoxLayout()
        self.add_segment_btn = QPushButton()
        self.add_segment_btn.setObjectName("primaryButton")
        self.add_segment_btn.clicked.connect(self._begin_segment_pair)
        segment_row.addWidget(self.add_segment_btn)
        self.exit_marker_btn = QPushButton()
        self.exit_marker_btn.setEnabled(False)
        self.exit_marker_btn.clicked.connect(self._exit_marker_mode)
        segment_row.addWidget(self.exit_marker_btn)
        self.undo_segment_btn = QPushButton()
        self.undo_segment_btn.clicked.connect(self._remove_last_segment)
        segment_row.addWidget(self.undo_segment_btn)
        self.delete_segment_btn = QPushButton()
        self.delete_segment_btn.setEnabled(False)
        self.delete_segment_btn.clicked.connect(self._remove_selected_segment)
        segment_row.addWidget(self.delete_segment_btn)
        self.clear_segments_btn = QPushButton()
        self.clear_segments_btn.clicked.connect(self._clear_segments)
        segment_row.addWidget(self.clear_segments_btn)
        self.segment_status = QLabel()
        segment_row.addWidget(self.segment_status, 1)
        center_layout.addLayout(segment_row)

        self.tabs = QTabWidget()
        self.score_widget = ScoreWidget()
        self.score_widget.marker_requested.connect(self._complete_score_marker)
        self.score_widget.marker_selected.connect(self._select_marker)
        self.score_widget.score_seek_requested.connect(self._seek_score_position)
        self.score_scroll = QScrollArea()
        self.score_scroll.setWidgetResizable(False)
        self.score_scroll.setWidget(self.score_widget)
        self.score_tab_index = self.tabs.addTab(self.score_scroll, "")

        practice = QWidget()
        p_layout = QVBoxLayout(practice)
        self.practice_hint = QLabel()
        self.practice_hint.setWordWrap(True)
        p_layout.addWidget(self.practice_hint)
        row = QHBoxLayout()
        self.bpm_title = QLabel()
        row.addWidget(self.bpm_title)
        self.bpm = QSpinBox()
        self.bpm.setRange(30, 240)
        self.bpm.setValue(90)
        row.addWidget(self.bpm)
        row.addStretch()
        p_layout.addLayout(row)
        self.practice_buttons = []
        for key in ("listen_demo", "practice_phrase", "record_score", "ai_advice"):
            button = QPushButton()
            if key == "listen_demo":
                button.clicked.connect(self.toggle_play)
            else:
                button.clicked.connect(lambda _=False, action_key=key: self._archived_feature(action_key))
            self.practice_buttons.append((key, button))
            p_layout.addWidget(button)
        p_layout.addStretch()
        self.practice_tab_index = self.tabs.addTab(practice, "")

        self.recovery_log = QTextEdit()
        self.recovery_log.setReadOnly(True)
        self.recovery_tab_index = self.tabs.addTab(self.recovery_log, "")
        center_layout.addWidget(self.tabs, 1)
        root.addWidget(center)
        root.setSizes([280, 1000])

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage(self._tr("started"))

    def _apply_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget { background: #171814; color: #ebe7dc; font-family: 'Microsoft YaHei UI'; font-size: 14px; }
            QMenuBar, QMenu { background: #20221d; }
            QListWidget, QTextEdit, QTabWidget::pane { background: #20221d; border: 1px solid #373a31; border-radius: 8px; }
            QListWidget::item { padding: 10px; }
            QListWidget::item:selected { background: #505b3d; }
            QPushButton { background: #34382e; border: 1px solid #555b49; border-radius: 8px; padding: 9px 14px; }
            QPushButton:hover { background: #424839; }
            QPushButton#primaryButton { background: #c8883b; color: #17120d; font-weight: 700; }
            QLabel#sectionTitle { font-size: 18px; font-weight: 700; }
            QLabel#heroTitle { font-size: 24px; font-weight: 700; padding: 8px 0; }
            QTabBar::tab { background: #282b24; padding: 9px 18px; }
            QTabBar::tab:selected { background: #505b3d; }
        """)

    def _set_language(self, language):
        if language not in TRANSLATIONS or language == self.language:
            return
        self.language = language
        self.settings.setValue("language", language)
        self._apply_language()

    def _display_song_title(self, song):
        preferred = song.get("title_zh") if self.language == "zh" else song.get("title_en")
        return preferred or song.get("title") or Path(song["folder"]).name

    def _refresh_song_titles(self):
        selected = self.song_list.currentRow()
        self.song_list.blockSignals(True)
        self.song_list.clear()
        for song in self.songs:
            self.song_list.addItem(self._display_song_title(song))
        self.song_list.blockSignals(False)
        if 0 <= selected < len(self.songs):
            self.song_list.setCurrentRow(selected)

    def _apply_language(self):
        self.setWindowTitle(self._tr("window_title"))
        self.file_menu.setTitle(self._tr("file"))
        self.language_menu.setTitle(self._tr("language"))
        self.import_action.setText(self._tr("import_local"))
        self.rescan_action.setText(self._tr("rescan"))
        self.chinese_action.setText(self._tr("chinese"))
        self.english_action.setText(self._tr("english"))
        self.library_title.setText(self._tr("library"))
        self.import_btn.setText(self._tr("import_song"))
        self.delete_song_btn.setText(self._tr("delete_song"))
        self.zoom_title.setText(self._tr("waveform_zoom"))
        self.reset_zoom_btn.setText(self._tr("reset_zoom"))
        self.add_segment_btn.setText(self._tr("add_marker"))
        self.exit_marker_btn.setText(self._tr("exit_marker"))
        self.undo_segment_btn.setText(self._tr("delete_last"))
        self.delete_segment_btn.setText(self._tr("delete_selected"))
        self.clear_segments_btn.setText(self._tr("clear_markers"))
        self.tabs.setTabText(self.score_tab_index, self._tr("score_tab"))
        self.tabs.setTabText(self.practice_tab_index, self._tr("practice_tab"))
        self.tabs.setTabText(self.recovery_tab_index, self._tr("recovery_tab"))
        self.practice_hint.setText(self._tr("practice_hint"))
        self.bpm_title.setText(self._tr("target_bpm"))
        for key, button in self.practice_buttons:
            button.setText(self._tr(key))
        self.recovery_log.setPlainText(self._tr("recovery_text"))
        self.waveform.set_language(self.language)
        self.score_widget.set_language(self.language)
        self._refresh_song_titles()
        self.song_title.setText(self._display_song_title(self.current_song) if self.current_song else self._tr("choose_song"))
        self._on_state(self.audio.playing)
        if self.current_song:
            self._refresh_segment_markers()
            self.statusBar().showMessage(self._tr("loaded", title=self._display_song_title(self.current_song)))
        else:
            self.segment_status.setText(self._tr("marker_disabled"))
            self.statusBar().showMessage(self._tr("started"))

    def reload_library(self):
        SONGS_DIR.mkdir(parents=True, exist_ok=True)
        self.songs.clear()
        self.song_list.clear()
        for folder in sorted(SONGS_DIR.iterdir()):
            if not folder.is_dir():
                continue
            audio = next((p for p in folder.iterdir() if p.suffix.lower() in SUPPORTED_AUDIO), None)
            images = [p for p in sorted(folder.iterdir()) if p.suffix.lower() in SUPPORTED_IMAGE]
            info = {}
            if (folder / "info.json").exists():
                try:
                    info = json.loads((folder / "info.json").read_text(encoding="utf-8"))
                except Exception:
                    pass
            if audio or images:
                song = {
                    "title": info.get("title", folder.name),
                    "title_zh": info.get("title_zh"),
                    "title_en": info.get("title_en"),
                    "audio": audio,
                    "images": images,
                    "bpm": info.get("bpm", 90),
                    "folder": folder,
                    "segments": info.get("paired_markers", []),
                    # Automatic layouts are deliberately recomputed so a new
                    # detector improves every score. Only a layout explicitly
                    # identified as manual is allowed to override detection.
                    "score_rows": info.get("score_rows", []) if info.get("score_rows_mode") == "manual" else [],
                }
                self.songs.append(song)
                self.song_list.addItem(self._display_song_title(song))
        self.statusBar().showMessage(self._tr("library_count", count=len(self.songs)))
        self.delete_song_btn.setEnabled(0 <= self.song_list.currentRow() < len(self.songs))

    def import_song(self):
        audio, _ = QFileDialog.getOpenFileName(self, self._tr("select_audio"), "", self._tr("audio_filter"))
        if not audio:
            return
        images, _ = QFileDialog.getOpenFileNames(self, self._tr("select_score"), "", self._tr("image_filter"))
        src = Path(audio)
        folder = SONGS_DIR / src.stem
        folder.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy2(src, folder / ("audio" + src.suffix.lower()))
        for i, image in enumerate(images, 1):
            image_src = Path(image)
            shutil.copy2(image_src, folder / f"tabs_{i}{image_src.suffix.lower()}")
        (folder / "info.json").write_text(json.dumps({"title": src.stem, "bpm": self.bpm.value()}, ensure_ascii=False, indent=2), encoding="utf-8")
        self.reload_library()

    def select_song(self, index):
        if index < 0 or index >= len(self.songs):
            self.delete_song_btn.setEnabled(False)
            return
        self.delete_song_btn.setEnabled(True)
        self.current_song = self.songs[index]
        self.pending_audio_marker_ms = None
        self.waveform.set_pending_marker(None)
        self._select_marker(-1)
        self._last_auto_scroll_row = None
        self.score_widget.set_playback_position(0, 0, [])
        self._set_marker_mode(False)
        self.segment_markers = list(self.current_song.get("segments", []))
        self.song_title.setText(self._display_song_title(self.current_song))
        self.bpm.setValue(int(self.current_song["bpm"] or 90))
        audio = self.current_song["audio"]
        if audio:
            try:
                waveform_samples = self.audio.load(audio)
                self.waveform.set_audio(waveform_samples, self.audio.duration_ms)
                self.zoom_slider.setValue(1)
                self._set_waveform_zoom(1)
                self.time_label.setText(f"00:00 / {self._fmt(self.audio.duration_ms)}")
            except Exception as exc:
                self.waveform.set_audio([])
                QMessageBox.critical(self, self._tr("audio_load_failed"), str(exc))
        images = self.current_song["images"]
        if images:
            self.score_widget.set_score(images[0], self.current_song.get("score_rows"))
            valid_rows = self.score_widget.row_boxes
            self.segment_markers = [
                marker for marker in self.segment_markers
                if 0 <= int(marker.get("row_index", -1)) < len(valid_rows)
                and "time_ms" in marker and "score_x" in marker
            ]
            for marker in self.segment_markers:
                top, bottom = valid_rows[int(marker["row_index"])]
                marker["row_top"] = top
                marker["row_bottom"] = bottom
        else:
            self.score_widget.clear_score()
        self._refresh_segment_markers()
        self.statusBar().showMessage(self._tr("loaded", title=self._display_song_title(self.current_song)))

    def delete_current_song(self):
        index = self.song_list.currentRow()
        if index < 0 or index >= len(self.songs):
            QMessageBox.information(self, self._tr("delete_song_title"), self._tr("delete_song_missing"))
            return
        song = self.songs[index]
        title = self._display_song_title(song)
        answer = QMessageBox.question(
            self,
            self._tr("delete_song_title"),
            self._tr("delete_song_question", title=title),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        folder = Path(song["folder"]).resolve()
        songs_root = SONGS_DIR.resolve()
        try:
            folder.relative_to(songs_root)
        except ValueError:
            QMessageBox.critical(self, self._tr("delete_song_failed"), str(folder))
            return
        try:
            self.audio.stop(reset=True)
            import shutil
            shutil.rmtree(folder)
        except Exception as exc:
            QMessageBox.critical(self, self._tr("delete_song_failed"), str(exc))
            return
        self.current_song = None
        self.segment_markers = []
        self.selected_marker_index = -1
        self.score_widget.clear_score()
        self.waveform.set_audio([])
        self.reload_library()
        if self.songs:
            self.song_list.setCurrentRow(min(index, len(self.songs) - 1))
        else:
            self.song_title.setText(self._tr("choose_song"))
            self.delete_song_btn.setEnabled(False)
        self.statusBar().showMessage(self._tr("library_count", count=len(self.songs)))

    def toggle_play(self):
        if not self.current_song or not self.current_song.get("audio"):
            QMessageBox.information(self, self._tr("notice"), self._tr("choose_audio_song"))
            return
        if self.audio.playing:
            self.audio.pause()
        else:
            self.audio.play()

    def _archived_feature(self, action_key):
        QMessageBox.information(self, self._tr(action_key), self._tr("archived_unavailable"))

    def _on_state(self, playing):
        self.play_btn.setText(self._tr("pause") if playing else self._tr("play_demo"))
        if playing:
            # Force one auto-scroll at the beginning of a new play session;
            # subsequent timer ticks only scroll when the score row changes.
            self._last_auto_scroll_row = None

    def _refresh_progress(self):
        duration = self.audio.duration_ms
        position = self.audio.position_ms
        ratio = position / duration if duration else 0.0
        self.waveform.set_progress(ratio)
        self.score_widget.set_playback_position(position, duration, self.segment_markers)
        self.time_label.setText(f"{self._fmt(position)} / {self._fmt(duration)}")
        # Do not fight the user's mouse-wheel scrolling. Auto-scroll only
        # once when playback enters a different score row, not on every
        # 50-ms progress refresh.
        row_index = self.score_widget.playback_row_index()
        if self.audio.playing and row_index is not None and row_index != self._last_auto_scroll_row:
            self._auto_scroll_score(row_index)
            self._last_auto_scroll_row = row_index
        if self.audio.playing and self.zoom_slider.value() > 1:
            bar = self.waveform_scroll.horizontalScrollBar()
            cursor_x = int(self.waveform.width() * ratio)
            left = bar.value()
            right = left + self.waveform_scroll.viewport().width()
            margin = 48
            if cursor_x < left + margin or cursor_x > right - margin:
                bar.setValue(max(0, cursor_x - self.waveform_scroll.viewport().width() // 2))

    def _auto_scroll_score(self, row_index=None):
        """Keep the score row containing the playback cursor visible."""
        if row_index is None:
            row_index = self.score_widget.playback_row_index()
        if row_index is None or not self.score_widget.row_boxes:
            return
        top_ratio, bottom_ratio = self.score_widget.row_boxes[row_index]
        y = int(((top_ratio + bottom_ratio) / 2) * self.score_widget.height())
        bar = self.score_scroll.verticalScrollBar()
        view_height = self.score_scroll.viewport().height()
        top, bottom = bar.value(), bar.value() + view_height
        margin = 60
        if y < top + margin or y > bottom - margin:
            bar.setValue(max(0, y - view_height // 2))

    def _select_marker(self, index):
        if index is None or not (0 <= int(index) < len(self.segment_markers)):
            self.selected_marker_index = -1
        else:
            self.selected_marker_index = int(index)
        self.waveform.set_selected_marker(self.selected_marker_index)
        self.score_widget.set_selected_marker(self.selected_marker_index)
        self.delete_segment_btn.setEnabled(self.selected_marker_index >= 0)
        if self.selected_marker_index >= 0:
            marker = self.segment_markers[self.selected_marker_index]
            self.segment_status.setText(
                self._tr("selected_marker", index=self.selected_marker_index + 1, time=self._fmt(int(marker["time_ms"])))
            )

    def _remove_selected_segment(self):
        if not (0 <= self.selected_marker_index < len(self.segment_markers)):
            return
        removed = self.segment_markers.pop(self.selected_marker_index)
        self.pending_audio_marker_ms = None
        self.waveform.set_pending_marker(None)
        self._save_segment_markers()
        self._refresh_segment_markers()
        self._select_marker(-1)
        self.segment_status.setText(self._tr("removed_marker", time=self._fmt(int(removed["time_ms"])), count=len(self.segment_markers)))

    def _seek_ratio(self, ratio):
        self.audio.seek_ms(int(self.audio.duration_ms * ratio))
        self._refresh_progress()

    def _seek_score_position(self, row_index, x_ratio):
        if not self.current_song or not self.current_song.get("audio") or not self.audio.duration_ms:
            return
        self.score_widget.set_playback_position(
            self.audio.position_ms,
            self.audio.duration_ms,
            self.segment_markers,
        )
        mapped = self.score_widget.score_position_to_time(row_index, x_ratio)
        if mapped is None:
            return
        time_ms = int(mapped if isinstance(mapped, (int, float)) and mapped > 1 else mapped * self.audio.duration_ms)
        self.audio.seek_ms(max(0, min(self.audio.duration_ms, time_ms)))
        self._refresh_progress()

    def _begin_segment_pair(self):
        if not self.current_song or not self.current_song.get("audio") or not self.current_song.get("images"):
            QMessageBox.information(self, self._tr("cannot_add"), self._tr("need_audio_score"))
            return
        self.pending_audio_marker_ms = None
        self.waveform.set_pending_marker(None)
        self._set_marker_mode(True)
        self.add_segment_btn.setEnabled(False)
        self.exit_marker_btn.setEnabled(True)
        self.tabs.setCurrentWidget(self.score_scroll)
        self.segment_status.setText(self._tr("marker_step1"))

    def _exit_marker_mode(self):
        self.pending_audio_marker_ms = None
        self.waveform.set_pending_marker(None)
        self._set_marker_mode(False)
        self.add_segment_btn.setEnabled(True)
        self.exit_marker_btn.setEnabled(False)
        self.segment_status.setText(self._tr("normal_mode", count=len(self.segment_markers)))

    def _set_pending_audio_marker(self, ratio):
        if not self.waveform.marker_mode:
            return
        marker_ms = int(self.audio.duration_ms * ratio)
        self.pending_audio_marker_ms = marker_ms
        self.waveform.set_pending_marker(marker_ms)
        self.audio.seek_ms(marker_ms)
        self._refresh_progress()
        self.segment_status.setText(
            self._tr("marker_step2", time=self._fmt(marker_ms))
        )

    def _complete_score_marker(self, x_ratio, y_ratio):
        if not self.score_widget.marker_mode:
            return
        if self.pending_audio_marker_ms is None:
            QMessageBox.information(self, self._tr("select_audio_first"), self._tr("select_audio_position"))
            return
        row_index = next(
            (index for index, (top, bottom) in enumerate(self.score_widget.row_boxes) if top <= y_ratio <= bottom),
            None,
        )
        if row_index is None:
            QMessageBox.warning(self, self._tr("outside_row"), self._tr("click_row"))
            return
        row_top, row_bottom = self.score_widget.row_boxes[row_index]
        new_marker = {
            "time_ms": int(self.pending_audio_marker_ms),
            "row_index": row_index,
            "score_x": round(float(x_ratio), 6),
            "row_top": round(float(row_top), 6),
            "row_bottom": round(float(row_bottom), 6),
        }
        self.segment_markers.append(new_marker)
        self.segment_markers.sort(key=lambda marker: int(marker["time_ms"]))
        inserted_index = next(index for index, marker in enumerate(self.segment_markers) if marker is new_marker)
        self.pending_audio_marker_ms = None
        self.waveform.set_pending_marker(None)
        self._save_segment_markers()
        self._refresh_segment_markers()
        self.segment_status.setText(
            self._tr("inserted_marker", index=inserted_index + 1)
        )

    def _refresh_segment_markers(self):
        audio_markers = [int(marker["time_ms"]) for marker in self.segment_markers]
        score_markers = [
            {
                "x": float(marker["score_x"]),
                "row_top": float(marker["row_top"]),
                "row_bottom": float(marker["row_bottom"]),
            }
            for marker in self.segment_markers
        ]
        self.waveform.set_markers(audio_markers)
        self.score_widget.set_markers(score_markers)
        if not self.waveform.marker_mode:
            self.segment_status.setText(self._tr("paired_count", count=len(self.segment_markers)))

    def _set_marker_mode(self, enabled):
        self.waveform.set_marker_mode(enabled)
        self.score_widget.set_marker_mode(enabled)
        self.add_segment_btn.setEnabled(not enabled)
        self.exit_marker_btn.setEnabled(enabled)

    def _save_segment_markers(self):
        if not self.current_song:
            return
        info_path = Path(self.current_song["folder"]) / "info.json"
        try:
            info = json.loads(info_path.read_text(encoding="utf-8")) if info_path.exists() else {}
        except Exception:
            info = {}
        info["paired_markers"] = self.segment_markers
        info["score_rows"] = [
            {"top": round(top, 6), "bottom": round(bottom, 6)}
            for top, bottom in self.score_widget.row_boxes
        ]
        info.setdefault("score_rows_mode", "auto")
        info_path.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
        self.current_song["segments"] = list(self.segment_markers)
        self.current_song["score_rows"] = list(info["score_rows"])

    def _remove_last_segment(self):
        if not self.segment_markers:
            return
        self.segment_markers.pop()
        self.pending_audio_marker_ms = None
        self.waveform.set_pending_marker(None)
        self._save_segment_markers()
        self._refresh_segment_markers()
        self._select_marker(-1)

    def _clear_segments(self):
        if not self.segment_markers:
            return
        answer = QMessageBox.question(self, self._tr("clear_title"), self._tr("clear_question"))
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.segment_markers.clear()
        self.pending_audio_marker_ms = None
        self.waveform.set_pending_marker(None)
        self._set_marker_mode(False)
        self._save_segment_markers()
        self._refresh_segment_markers()
        self._select_marker(-1)

    def _set_waveform_zoom(self, value):
        value = max(1, int(value))
        self.zoom_label.setText(f"{value}×")
        viewport_width = max(640, self.waveform_scroll.viewport().width())
        old_ratio = self.audio.position_ms / self.audio.duration_ms if self.audio.duration_ms else 0.0
        self.waveform.setFixedWidth(viewport_width * value)
        self.waveform.update()
        bar = self.waveform_scroll.horizontalScrollBar()
        QTimer.singleShot(0, lambda: bar.setValue(max(0, int(self.waveform.width() * old_ratio - self.waveform_scroll.viewport().width() / 2))))

    def _audio_error(self, message):
        QMessageBox.critical(self, self._tr("play_failed"), self._tr("audio_device_failed", message=message))

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace) and self.selected_marker_index >= 0:
            self._remove_selected_segment()
            event.accept()
            return
        super().keyPressEvent(event)

    def closeEvent(self, event):
        self.audio.stop()
        super().closeEvent(event)

    @staticmethod
    def _fmt(milliseconds):
        seconds = max(0, milliseconds // 1000)
        return f"{seconds // 60:02d}:{seconds % 60:02d}"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
