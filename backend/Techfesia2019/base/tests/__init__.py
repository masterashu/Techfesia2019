import unittest


def suite():
    return unittest.TestLoader().discover("base.tests", pattern="*.py")
