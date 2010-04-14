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
    """
    
    index = patch.find('\ndiff')
    if index == -1:
        return patch
    return patch[index+1:]

def get_patch_with_header(attachment):
    patch = strip_patch_header(attachment.data)
    lines = ['# HG changeset patch',
             '# User %s <%s>' % (attachment.attacher.real_name,
                                 attachment.attacher.email),
             'Bug %d - %s' % (attachment.bug.id,
                              attachment.bug.summary),
             '',
             patch]
    return '\n'.join(lines)

def get_patch(bug):
    def cmp_lastcreated(a, b):
        return cmp(a.creation_time, b.creation_time)

    patches = [patch for patch in bug.attachments
               if patch.is_patch and not patch.is_obsolete]
    patches.sort(cmp_lastcreated)

    most_recent_patch = patches[-1]

    return get_patch_with_header(most_recent_patch)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "usage: %s <post|get> <bug-id>" % sys.argv[0]
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

    bzapi = bugzilla.BugzillaApi()
    bug = bzapi.bugs.get(bug_id)

    if cmd == 'get':
        print get_patch(bug)
    else:
        raise NotImplementedError('TODO: finish this!')
