#! /usr/bin/env python

import sys
import datetime
import base64
import optparse

import bugzilla

PULL_REQ_TEMPLATE = """<!DOCTYPE html>
<meta charset="utf-8">
<meta http-equiv="refresh" content="5;{URL}">
<title>Bugzilla Code Review</title>
<p>You can review this patch at <a href="{URL}">{URL}</a>,
or wait 5 seconds to be redirected there automatically.</p>"""

def make_pull_req_html(url):
    """
    >>> make_pull_req_html('http://foo.com/pull/1')
    '<!DOCTYPE html>\\n<meta charset="utf-8">\\n<meta http-equiv="refresh" content="5;http://foo.com/pull/1">\\n<title>Bugzilla Code Review</title>\\n<p>You can review this patch at <a href="http://foo.com/pull/1">http://foo.com/pull/1</a>,\\nor wait 5 seconds to be redirected there automatically.</p>'
    """

    return PULL_REQ_TEMPLATE.replace("{URL}", url)

def strip_patch_header(patch):
    """
    >>> strip_patch_header('#HG blarg\\n\\ndiff --git\\n')
    'diff --git\\n'

    >>> strip_patch_header('sup')
    'sup'

    >>> print strip_patch_header('diff --git\\n'
    ...                          'bleh\\n'
    ...                          'diff --git\\n'
    ...                          'yo')
    diff --git
    bleh
    diff --git
    yo
    """

    if patch.startswith('diff'):
        return patch
    index = patch.find('\ndiff')
    if index == -1:
        return patch
    return patch[index+1:]

def make_patch_header(real_name, email, bug_id, summary):
    """
    >>> print make_patch_header('Bob', 'bob@foo.com', 5, 'yo')
    # HG changeset patch
    # User Bob <bob@foo.com>
    Bug 5 - yo
    """

    lines = ['# HG changeset patch',
             '# User %s <%s>' % (real_name, email),
             'Bug %d - %s' % (bug_id, summary)]
    return '\n'.join(lines)

def make_patch(patch, real_name, email, bug_id, summary):
    """
    >>> print make_patch('hi', 'Bob', 'bob@foo.com', 5, 'yo')
    # HG changeset patch
    # User Bob <bob@foo.com>
    Bug 5 - yo
    <BLANKLINE>
    hi
    """

    patch = strip_patch_header(patch)
    header = make_patch_header(real_name, email, bug_id, summary)
    return '\n'.join([header, '', patch])

def get_patch_from_attachment(attachment):
    return make_patch(patch=attachment.data,
                      real_name=attachment.attacher.real_name,
                      email=attachment.attacher.email,
                      bug_id=attachment.bug.id,
                      summary=attachment.bug.summary)

def get_patch(bug):
    def cmp_lastcreated(a, b):
        return cmp(a.creation_time, b.creation_time)

    patches = [patch for patch in bug.attachments
               if patch.is_patch and not patch.is_obsolete]
    patches.sort(cmp_lastcreated)

    most_recent_patch = patches[-1]

    return get_patch_from_attachment(most_recent_patch)

def post_patch(bzapi, bug, patch, description, flags=None):
    """
    >>> bzapi = MockBugzillaApi({'username': 'avarma@mozilla.com'})
    >>> bzapi.request.mock_returns = TEST_USER_SEARCH_RESULT
    >>> bug = bugzilla.Bug(TEST_BUG, bzapi)
    >>> print post_patch(bzapi, bug, 'o hai', 'my patch')
    Called bzapi.request(
        'GET',
        '/user',
        query_args={'match': u'avarma@mozilla.com'})
    Called bzapi.request(
        'POST',
        '/bug/558680/attachment',
        body={'is_obsolete': False, 'flags': [], 'description': 'my patch', 'content_type': 'text/plain', 'encoding': 'base64', 'file_name': 'bug-558680-patch.diff', 'is_patch': True, 'data': 'IyBIRyBjaGFuZ2VzZXQgcGF0Y2gKIyBVc2VyIEF0dWwgVmFybWEgWzphdHVsXSA8YXZhcm1hQG1vemlsbGEuY29tPgpCdWcgNTU4NjgwIC0gSGVyZSBpcyBhIHN1bW1hcnkKCm8gaGFp', 'is_private': False, 'size': 105})
    # HG changeset patch
    # User Atul Varma [:atul] <avarma@mozilla.com>
    Bug 558680 - Here is a summary
    <BLANKLINE>
    o hai
    """

    full_patch = make_patch(patch=patch,
                            real_name=bzapi.current_user.real_name,
                            email=bzapi.current_user.email,
                            bug_id=bug.id,
                            summary=bug.summary)
    bzapi.attachments.post(bug_id=bug.id,
                           contents=full_patch,
                           filename="bug-%d-patch.diff" % bug.id,
                           description=description,
                           content_type='text/plain',
                           is_patch=True,
                           flags=flags)
    return full_patch

def post_pullreq(bzapi, bug, url, flags=None):
    """
    >>> bzapi = MockBugzillaApi({'username': 'avarma@mozilla.com'})
    >>> bug = bugzilla.Bug(TEST_BUG, bzapi)
    >>> post_pullreq(bzapi, bug, 'http://foo.com/pull/1')
    Called bzapi.request(
        'POST',
        '/bug/558680/attachment',
        body={'is_obsolete': False, 'flags': [], 'description': 'Pointer to pull request', 'content_type': 'text/html', 'encoding': 'base64', 'file_name': 'bug-558680-pullreq.html', 'is_patch': False, 'data': 'PCFET0NUWVBFIGh0bWw+CjxtZXRhIGNoYXJzZXQ9InV0Zi04Ij4KPG1ldGEgaHR0cC1lcXVpdj0icmVmcmVzaCIgY29udGVudD0iNTtodHRwOi8vZm9vLmNvbS9wdWxsLzEiPgo8dGl0bGU+QnVnemlsbGEgQ29kZSBSZXZpZXc8L3RpdGxlPgo8cD5Zb3UgY2FuIHJldmlldyB0aGlzIHBhdGNoIGF0IDxhIGhyZWY9Imh0dHA6Ly9mb28uY29tL3B1bGwvMSI+aHR0cDovL2Zvby5jb20vcHVsbC8xPC9hPiwKb3Igd2FpdCA1IHNlY29uZHMgdG8gYmUgcmVkaXJlY3RlZCB0aGVyZSBhdXRvbWF0aWNhbGx5LjwvcD4=', 'is_private': False, 'size': 287})
    """

    bzapi.attachments.post(bug_id=bug.id,
                           contents=make_pull_req_html(url),
                           filename="bug-%d-pullreq.html" % bug.id,
                           description="Pointer to pull request",
                           flags=flags,
                           content_type="text/html")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print ("usage: %s <post|get|pullreq> <bug-id> [desc] [url] "
               "[review requestee]" % sys.argv[0])
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd not in ['get', 'post', 'pullreq']:
        print "unrecognized command: %s" % cmd
        sys.exit(1)

    try:
        bug_id = int(sys.argv[2])
    except ValueError:
        print "not a valid bug id: %s" % sys.argv[2]
        sys.exit(1)

    if len(sys.argv) < 4:
        if cmd == 'post':
            print "patch description required."
            sys.exit(1)
        elif cmd == 'pullreq':
            print "pull request URL required."
            sys.exit(1)

    flags = []
    if len(sys.argv) >= 5:
        flags = [{"type_id": 4,
                  "name": "review",
                  "requestee": {"name": sys.argv[4]},
                  "status": "?"}]

    bzapi = bugzilla.BugzillaApi()
    bug = bzapi.bugs.get(bug_id)

    if cmd == 'get':
        sys.stdout.write(get_patch(bug))
    elif cmd == 'post':
        post_patch(bzapi=bzapi,
                   bug=bug,
                   patch=sys.stdin.read(),
                   description=sys.argv[3],
                   flags=flags)
    elif cmd == 'pullreq':
        post_pullreq(bzapi=bzapi,
                     bug=bug,
                     url=sys.argv[3],
                     flags=flags)
