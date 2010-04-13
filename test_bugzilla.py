import doctest
import unittest

from minimock import Mock
import bugzilla

CFG_WITH_LOGIN = {'api_server': 'http://foo/latest',
                  'username': 'bar',
                  'password': 'baz'}

class Tests(unittest.TestCase):
    pass

def test_upload(self):
    """
    >>> jsonreq = Mock('jsonreq')
    >>> jsonreq.mock_returns = {
    ...   "status": 201,
    ...   "body": {"ref": "http://foo/latest/attachment/1"},
    ...   "reason": "Created",
    ...   "content_type": "application/json"
    ... }
    >>> bzapi = bugzilla.BugzillaApi(config=CFG_WITH_LOGIN,
    ...                              jsonreq=jsonreq)
    >>> bzapi.post_attachment(bug_id=536619,
    ...                       contents="testing!",
    ...                       filename="contents.txt",
    ...                       description="test upload")
    Called jsonreq(
        body={'is_obsolete': False, 'flags': [],
              'description': 'test upload',
              'content_type': 'text/plain', 'encoding': 'base64',
              'file_name': 'contents.txt', 'is_patch': False,
              'data': 'dGVzdGluZyE=', 'is_private': False,
              'size': 8},
        method='POST',
        query_args={'username': 'bar', 'password': 'baz'},
        url='http://foo/latest/bug/536619/attachment')
    {'ref': 'http://foo/latest/attachment/1'}
    """

    pass

def get_tests_in_module(module):
    tests = []

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(module)
    for test in suite:
        tests.append(test)

    optionflags = (doctest.NORMALIZE_WHITESPACE |
                   doctest.REPORT_UDIFF)
    finder = doctest.DocTestFinder()
    doctests = finder.find(module)
    for test in doctests:
        if len(test.examples) > 0:
            tests.append(doctest.DocTestCase(test,
                                             optionflags=optionflags))

    return tests

def run_tests(verbosity=2):
    module = __import__(__name__)
    tests = get_tests_in_module(module)
    suite = unittest.TestSuite(tests)
    runner = unittest.TextTestRunner(verbosity=verbosity)
    runner.run(suite)

if __name__ == '__main__':
    run_tests()
