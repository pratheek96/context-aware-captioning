from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest


class UITests(unittest.TestCase):
    def test_sample_edit_export_flow(self):
        app = AppTest.from_file(str(Path(__file__).parents[1] / "app.py"))
        app.run(timeout=30)
        self.assertFalse(app.exception)
        next(b for b in app.button if b.label == "Load sample project").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.session_state["project"].captions), 4)
        first_name = next(t for t in app.text_input if t.label == "SPEAKER_00")
        first_name.set_value("Presenter")
        next(b for b in app.button if b.label == "Save speaker names").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["project"].speakers["SPEAKER_00"], "Presenter")
        next(b for b in app.button if b.label == "Save caption edits").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["project"].captions[0].original_text,
                         "Welcome to our captioning project.")
