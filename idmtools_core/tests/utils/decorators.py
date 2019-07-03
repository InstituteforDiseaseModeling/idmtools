import os
import unittest

comps_test = unittest.skipIf(
    os.environ.get('NO_COMPS_TESTS', False), 'No COMPS testing'
)
