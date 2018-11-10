import unittest, os
from os import getenv as env

testmodules = [
    'tests.unit.interface',
    'tests.unit.engine',
]

loader = unittest.TestLoader()

for t in testmodules:
    try:
        # If the module defines a suite() function, call it to get the suite.
        suite = loader.discover(t)
        mod = __import__(t, globals(), locals(), ['suite'])
        suitefn = getattr(mod, 'suite')
        suite.addTest(suitefn())
    except (ImportError, AttributeError):
        # else, just load all the test cases from the module.
        suite.addTest(unittest.defaultTestLoader.loadTestsFromName(t))

    unittest.TextTestRunner().run(suite)