# Installation

First, run the unit tests to make sure everything works okay:

    python test_bugzilla.py

Then make a symlink to `bzpatch`, the command-line tool:

    ln -s bzpatch.py ~/bin/bzpatch

Now create a file called `~/.bugzilla-config.json` and fill it out with something like this:

    {
      "username": "me@email.com"
    , "password": "foo"
    }

If you really don't like the idea of leaving your Bugzilla password in a plaintext file on your computer, you can leave out the `password` key and you'll just be prompted for your password every time you use `bzpatch`. You might also want to contact the Bugzilla team and ask them to implement OAuth or something to make this process both convenient and secure.

# Usage

## Posting or applying a patch

Assuming you're in a Mercurial repository and have made some changes to it, you can pipe `hg diff` output into `bzpatch post` like so:

    hg diff | bzpatch post 12345 "first patch attempt"

This posts the diff as a patch attachment to bug 12345 with the name/description "first patch attempt". The patch also contains HG-specific headers that provide information about the author, bug number, and bug summary.

Note that `bzpatch post` doesn't actually request review from anyone; nor does it automatically obsolete any earlier patches.

You can apply the above patch by piping the output of `bzpatch get`:

    bzpatch get 12345 | hg import -

Note that once the patch is imported, the changeset author is already set to your Bugzilla username/email, and the changeset description contains the name and number of the bug, thanks to the HG-specific headers that were in the patch file.

Note that `bzpatch get` automatically retrieves that most recently uploaded patch, if multiple ones are found.

## Posting a pointer to a GitHub pull request

Some Mozilla projects are starting to use GitHub with Bugzilla, and pull requests are much easier to deal with than patches. One way to deal effectively with this hybrid development process is to upload an attachment to a bug that is simply a "pointer" to a GitHub pull request. For an example of this, see [bug 610816].

To automatically post such a request, you can do this:

    bzpatch pullreq 610816 https://github.com/mozilla/addon-sdk/pull/49

Note that, like `bzpatch post`, this command doesn't automatically request review or obsolete older attachments.

  [bug 610816]: https://bugzilla.mozilla.org/show_bug.cgi?id=610816
