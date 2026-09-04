import sys
import unittest
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import QApplication

from main_window import MainWindow, ScoreWidget


class ScoreRowDetectionTests(unittest.TestCase):
    def test_greensleeves_standard_and_tab_pairs_are_four_rows(self):
        image = APP_DIR / "songs" / "greensleeves" / "tabs_1.png"
        self.assertEqual(4, len(ScoreWidget._detect_rows(str(image))))

    def test_aguado_standard_staves_remain_five_rows(self):
        image = APP_DIR / "songs" / "aguado_op3_no3" / "tabs_1.png"
        self.assertEqual(5, len(ScoreWidget._detect_rows(str(image))))

    def test_dense_carcassi_standard_staves_remain_ten_rows(self):
        image = APP_DIR / "songs" / "carcassi_etude_1" / "tabs_1.png"
        self.assertEqual(10, len(ScoreWidget._detect_rows(str(image))))

    def test_greensleeves_content_bounds_do_not_regress(self):
        image = APP_DIR / "songs" / "greensleeves" / "tabs_1.png"
        rows = ScoreWidget._detect_rows(str(image))
        bounds = ScoreWidget._detect_row_content_bounds(str(image), rows)
        self.assertEqual(4, len(bounds))
        for left, right in bounds:
            self.assertAlmostEqual(0.0894, left, delta=0.008)
            self.assertGreater(right, 0.94)

    def test_aguado_continuation_rows_start_near_the_staff_header(self):
        image = APP_DIR / "songs" / "aguado_op3_no3" / "tabs_1.png"
        rows = ScoreWidget._detect_rows(str(image))
        bounds = ScoreWidget._detect_row_content_bounds(str(image), rows)
        self.assertEqual(5, len(bounds))
        self.assertGreater(bounds[0][0], 0.14)  # indented first system
        for left, right in bounds[1:]:
            self.assertAlmostEqual(0.0927, left, delta=0.012)
            self.assertGreater(right, 0.94)

    def test_valid_confirmed_rows_are_preserved(self):
        rows = [{"top": 0.1, "bottom": 0.2}, {"top": 0.3, "bottom": 0.4}]
        self.assertEqual([(0.1, 0.2), (0.3, 0.4)], ScoreWidget._normalize_confirmed_rows(rows))

    def test_overlapping_confirmed_rows_are_rejected(self):
        rows = [{"top": 0.1, "bottom": 0.3}, {"top": 0.2, "bottom": 0.4}]
        self.assertEqual([], ScoreWidget._normalize_confirmed_rows(rows))

    def test_score_seek_without_markers_is_monotonic_across_rows(self):
        widget = ScoreWidget()
        widget.row_boxes = [(0.1, 0.2), (0.3, 0.4), (0.5, 0.6)]
        widget.row_content_boxes = [(0.1, 0.9)] * 3
        first = widget.score_position_to_time(0, 0.1)
        middle = widget.score_position_to_time(1, 0.5)
        last = widget.score_position_to_time(2, 0.9)
        self.assertLess(first, middle)
        self.assertLess(middle, last)

    def test_score_seek_with_tracks_uses_paired_audio_time(self):
        widget = ScoreWidget()
        widget.row_boxes = [(0.1, 0.2), (0.3, 0.4)]
        widget.row_content_boxes = [(0.1, 0.9), (0.1, 0.9)]
        widget.playback_tracks = [(1000, 3000, 0, 0.2, 0.8)]
        self.assertEqual(2000, widget.score_position_to_time(0, 0.5))


class BilingualInterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_language_switch_updates_controls_and_song_titles(self):
        window = MainWindow()
        window._set_language("en")
        self.assertEqual("Guitar Learning Assistant", window.windowTitle())
        self.assertEqual("My Library", window.library_title.text())
        self.assertEqual("语言", window.language_menu.title())
        self.assertIn("Spanish Romance", [window.song_list.item(i).text() for i in range(window.song_list.count())])
        window._set_language("zh")
        self.assertEqual("吉他学习助手", window.windowTitle())
        self.assertEqual("我的曲库", window.library_title.text())
        self.assertEqual("Language", window.language_menu.title())
        self.assertIn("爱的罗曼史", [window.song_list.item(i).text() for i in range(window.song_list.count())])
        window.close()

    def test_space_shortcut_is_window_wide_and_does_not_auto_repeat(self):
        window = MainWindow()
        self.assertEqual(QKeySequence(Qt.Key.Key_Space), window.play_pause_shortcut.key())
        self.assertEqual(Qt.ShortcutContext.WindowShortcut, window.play_pause_shortcut.context())
        self.assertFalse(window.play_pause_shortcut.autoRepeat())
        self.assertTrue(hasattr(window, "delete_song_btn"))
        self.assertFalse(window.delete_song_btn.isEnabled())
        window.close()


if __name__ == "__main__":
    unittest.main()
