import os
import tempfile
import unittest

from main import preview_png


class PreviewFeatureTest(unittest.TestCase):
    def test_preview_png_creates_svg_and_preview_png(self):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        input_png = os.path.join(repo_root, 'input', 'letter_H.png')

        with tempfile.TemporaryDirectory() as tmp_dir:
            svg_path, preview_path, viewer_path = preview_png(input_png, tmp_dir)

            self.assertTrue(os.path.exists(svg_path))
            self.assertTrue(os.path.exists(preview_path))
            self.assertTrue(os.path.exists(viewer_path))
            self.assertTrue(svg_path.endswith('.svg'))
            self.assertTrue(preview_path.endswith('.png'))
            self.assertTrue(viewer_path.endswith('_viewer.html'))


if __name__ == '__main__':
    unittest.main()
