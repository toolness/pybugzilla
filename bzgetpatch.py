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

if __name__ == '__main__':
    bug_id = int(sys.argv[1])
    bzapi = bugzilla.BugzillaApi()
    bug = bugzilla.Bug.fetch(bzapi, bug_id)

    def cmp_lastcreated(a, b):
        return cmp(a.creation_time, b.creation_time)

    patches = [patch for patch in bug.attachments
               if patch.is_patch and not patch.is_obsolete]
    patches.sort(cmp_lastcreated)

    most_recent_patch = patches[-1]

    print get_patch_with_header(most_recent_patch)
