import sys
import os
import unittest
sys.path.append(os.path.abspath('../core'))
from core.model.detection import Detector

class TestDetection(unittest.TestCase):

    def setUp(self):
        self.dt = Detector()

    def tearDown(self):
        del self.dt

    def test_choose_classifiers(self):
        methods = ["k-nearest neighbors", "support vector machine"]
        #methods = ["random forest", "perceptron"]

        _ = self.dt.choose_classifiers(list(range(5, 7)))
        #_ = self.dt.choose_classifiers([1, 9])

        self.assertListEqual(self.dt.methods, methods)

if __name__ == '__main__':
    unittest.main()