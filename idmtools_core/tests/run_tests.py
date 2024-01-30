import os
import sys
import glob
import unittest
import xmlrunner

root_idmtools = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

sys.path.insert(0, os.path.abspath(os.path.join(root_idmtools, "idmtools_models")))
sys.path.insert(0, os.path.abspath(os.path.join(root_idmtools, "idmtools_core")))


def create_test_suite():
    test_file_strings = glob.glob('./test_*.py')
    module_strings = [str[2:len(str) - 3] for str in test_file_strings]
    suites = [unittest.defaultTestLoader.loadTestsFromName(name) for name in module_strings]
    testSuite = unittest.TestSuite(suites)
    return testSuite


testSuite = create_test_suite()
# text_runner = unittest.TextTestRunner().run(testSuite)
xml_runner = xmlrunner.XMLTestRunner(output="reports")
results = xml_runner.run(testSuite)
