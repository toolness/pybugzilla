#! /usr/bin/env python

import sys
import datetime
import base64

import bugzilla

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

def post_patch(bzapi, bug, patch, description):
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
                           is_patch=True)
    return full_patch

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "usage: %s <post|get> <bug-id> [desc]" % sys.argv[0]
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd not in ['get', 'post']:
        print "unrecognized command: %s" % cmd
        sys.exit(1)

    try:
        bug_id = int(sys.argv[2])
    except ValueError:
        print "not a valid bug id: %s" % sys.argv[2]
        sys.exit(1)

    if cmd == 'post' and len(sys.argv) < 4:
        print "patch description required."
        sys.exit(1)

    bzapi = bugzilla.BugzillaApi()
    bug = bzapi.bugs.get(bug_id)

    if cmd == 'get':
        sys.stdout.write(get_patch(bug))
    else:
        post_patch(bzapi=bzapi,
                   bug=bug,
                   patch=sys.stdin.read(),
                   description=sys.argv[3])
