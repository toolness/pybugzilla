import os
import doctest
import unittest

from minimock import Mock
import bugzilla

TEST_CFG_WITH_LOGIN = {'api_server': 'http://foo/latest',
                       'username': 'bar',
                       'password': 'baz'}

TEST_USER = {
    u'email': u'avarma@mozilla.com', u'real_name': u'Atul Varma [:atul]',
    u'can_login': u'1', u'name': u'avarma@mozilla.com',
    u'id': u'298253'
    }

TEST_USER_SEARCH_RESULT = {
    u'users': [TEST_USER]
}

TEST_ATTACHMENT_WITHOUT_DATA = {
    u'is_obsolete': u'0',
    u'description': u'test upload', u'encoding': u'base64',
    u'file_name': u'contents.txt', u'is_patch': u'0',
    u'creation_time': u'2010-04-13T18:02:00Z',
    u'bug_id': u'536619',
    u'last_change_time': u'2010-04-13T18:02:00Z',
    u'content_type': u'text/plain',
    u'attacher': {u'name': u'avarma'}, u'is_url': u'0',
    u'id': u'438797', u'is_private': u'0',
    u'size': u'8'
}

TEST_ATTACHMENT_WITH_DATA = {
    u'is_obsolete': u'0',
    u'description': u'test upload', u'encoding': u'base64',
    u'file_name': u'contents.txt', u'is_patch': u'0',
    u'creation_time': u'2010-04-13T18:02:00Z',
    u'data': u'dGVzdGluZyE=', u'bug_id': u'536619',
    u'last_change_time': u'2010-04-13T18:02:00Z',
    u'content_type': u'text/plain',
    u'attacher': {u'name': u'avarma'}, u'is_url': u'0',
    u'id': u'438797', u'is_private': u'0',
    u'size': u'8'
}

TEST_BUG = {
    u'attachments':
        [{u'is_obsolete': u'0',
          u'description': u'here is a description',
          u'file_name': u'traceback-on-package-exception',
          u'is_patch': u'1', u'creation_time': u'2010-04-11T19:16:00Z',
          u'last_change_time': u'2010-04-11T19:16:59Z',
          u'bug_id': u'558680', u'content_type': u'text/plain',
          u'attacher': {u'name': u'asqueella'},
          u'id': u'438381', u'size': u'1320'}],
    u'summary': u'Here is a summary',
    u'id': u'558680'
    }

TEST_BUG_NO_ATTACHMENTS = {
    u'summary': u'Here is another summary',
    u'id': u'558681'
    }

class MockBugzillaApi(bugzilla.BugzillaApi):
    def __init__(self, config=None):
        if config is None:
            config = {}
        bugzilla.BugzillaApi.__init__(self,
                                      config=config,
                                      jsonreq=Mock('jsonreq'),
                                      getpass=Mock('getpass'))
        self.request = Mock('bzapi.request')

DOCTEST_EXTRA_GLOBS = {
    'Mock': Mock,
    'MockBugzillaApi': MockBugzillaApi
    }

for globname in globals().keys():
    if globname.startswith('TEST_'):
        DOCTEST_EXTRA_GLOBS[globname] = globals()[globname]
del globname

class Tests(unittest.TestCase):
    # TODO: Add unit tests here.
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
    doctests = finder.find(module, extraglobs=DOCTEST_EXTRA_GLOBS)
    for test in doctests:
        if len(test.examples) > 0:
            tests.append(doctest.DocTestCase(test,
                                             optionflags=optionflags))

    return tests

def run_tests(verbosity=2):
    modules = [filename[:-3] for filename in os.listdir('.')
               if filename.endswith('.py')
               and filename not in ['minimock.py']]
    tests = []
    for modulename in modules:
        module = __import__(modulename)
        tests.extend(get_tests_in_module(module))

    suite = unittest.TestSuite(tests)
    runner = unittest.TextTestRunner(verbosity=verbosity)
    runner.run(suite)

if __name__ == '__main__':
    run_tests()
