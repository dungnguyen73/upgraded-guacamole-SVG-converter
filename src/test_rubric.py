import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

import test_compare


class EvaluationRubricTests(unittest.TestCase):
    def test_classifies_excellent_thresholds(self):
        label = test_compare.classify_result(iou=0.82, dice=0.90, recon_out=0.95)
        self.assertEqual(label, "Excellent")

    def test_classifies_good_thresholds(self):
        label = test_compare.classify_result(iou=0.70, dice=0.80, recon_out=0.91)
        self.assertEqual(label, "Good")

    def test_classifies_average_thresholds(self):
        label = test_compare.classify_result(iou=0.55, dice=0.70, recon_out=0.86)
        self.assertEqual(label, "Average")

    def test_classifies_poor_thresholds(self):
        label = test_compare.classify_result(iou=0.40, dice=0.60, recon_out=0.80)
        self.assertEqual(label, "Poor")


if __name__ == "__main__":
    unittest.main()
