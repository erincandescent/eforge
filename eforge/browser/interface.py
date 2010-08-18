# -*- coding: utf-8 -*-
# EForge project management system, Copyright © 2010, Element43
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

from django.contrib.auth.models import User

class IRepository(object):
    """
        EForge source browser repository access interface.

        This is the interface by which EForge will access (to inspect) the
        repository.
    """

    def __init__(self, path):
        """
            Constructs a new Repository object. path should be the path to the
            repository being opened.
        """


    @property
    def branches(self):
        """
            Returns a dictionary containing a key for every branch in the
            repository with a corresponding value for that branch's head
            revision

            The head-revision should be returned as an IRevision subclass.

            If branches are not supported, should return an empty list.
        """
        pass

    @property
    def tags(self):
        """
            Returns a dictionary containing a key for every tag in the
            repository with a corresponding value for that tag's revision

            The revision should be returned as an IRevision subclass.

            If tags are not supported, should return an empty list.
        """
        pass

    def revision(self, id):
        """
            Given the specified id, returns a revision (IRevision) object
            corresponding to it.
        """
        pass

    @property
    def head(self):
        """
            Returns the head revision of the repository. This is commonly the
            most recent revision on the "head" or "trunk" branch.

            For example, for Git this would be the revision pointed to by the
            "HEAD" ref; on Subversion this would be the last commit to "trunk".
        """
        pass

    @property
    def revisions(self, num):
        """
            Returns a list of the latest \p num revisions in the repository. The
            order is reverse chronological.

            Because revision lists can grow quite large, it is recommended that
            implementations use a custom iterator to avoid loading the whole
            repository into memory.
        """

class IRevision(object):
    """
        Repository changeset/revision.
    """

    @property
    def id(self):
        """
            The ID of this revision. This should be a string identifying the
            revision which can be later passed to IRepository.revision in order
            to get an object corresponding to the same revision.
        """
        pass

    @property
    def short_id(self):
        """
            The short ID of this revision. This should be a shortened (but
            nontheless unambiguous) ID for a revision in the repository, which
            it should be possible to use in the same way the value of id would
            be.

            Some systems (Such as Subversion) have concise monotonic IDs and
            should return the same value for short_id and id. Others,
            particularly distributed systems (Such as hg and git) use 40
            character SHA-1 hashes as identifiers; in these cases it is valuable
            to return a truncated version for brevity.

            The default implementation returns id.
        """
        return self.id

    @property
    def author_email(self):
        """
            Returns the E-Mail address of the author (if known)
        """
        pass

    @property
    def author_name(self):
        """
            Returns the name of the author (if known)
        """
        return self.author_email

    @property
    def author_user(self):
        """
            Returns the user of the author (if known)
        """
        try:
            return User.objects.get(email=self.author_email)
        except User.NotFoundException:
            return None

    @property
    def message(self):
        """ Commit message """
        pass

    @property
    def short_message(self):
        """ Short message """
        try:
            return self.message.split('.', 1)[0].strip()
        except:
            return self.message

    @property
    def parents(self):
        """
            Returns a list of the revisions that this revision is descended from.
        """
        pass

    @property
    def children(self):
        """
            Returns a list of the revisions that are descended from this revision.
        """
        pass

    @property
    def root(self):
        """
            The root directory of this revision
        """
        pass

class IGenericFile(object):
    """
        A generic file object. This is the base class of IDirectory and
        IFile. It provides some trivial methods.
    """

    def __init__(self, parent, name):
        """
            Constructs the generic file. parent should be the directory which
            is parent of this one (if not the root, in which case pass None).

            The name parameter should be the name of the file relative to the
            parent directory. For the root, the name is ignored
        """
        if parent:
            self.path   = parent.path + '/' + name
            self.name   = name
            self.pretty = self.path
        else:
            self.path   = ''
            self.name   = None
            self.pretty = 'Root'

    @property
    def is_file(self):
        """
            Is this a file?
        """
        return not self.is_directory

    @property
    def is_directory(self):
        """
            Is this a directory?
        """
        return not self.is_file

class IDirectory(IGenericFile):
    """
        A directory within the repository
    """
    def __init__(self, *args, **kwargs):
        IGenericFile.__init__(self, *args, **kwargs)

    @property
    def is_directory(self):
        return True


    @property
    def children(self):
        """ A list of the immediate children of this directory """
        pass

    def child(self, name):
        """ Get the child with the given name"""
        pass

class IFile(IGenericFile):
    """
        A file within the repository.

        In addition to the methods documented here, this should be implemented
        as a file-like object. Before any of the file methods can be called,
        the "open" method must be invoked to permit lazy loading and
        initialization.

        Finally, the "data" property should be a string of the contents of the
        file
    """

    def __init__(self, *args, **kwargs):
        IGenericFile.__init__(self, *args, **kwargs)
        self.__analysed = False

    @property
    def is_file(self):
        return True

    @property
    def size(self):
        """ The size, in bytes, of the file """
        pass

    @property
    def is_binary(self):
        """
            Is this a binary file?

            For systems which do not track this, a herustic is provided.
        """
        if not self.__analysed:
            self.__file_type()
        return self.__is_binary

    @property
    def is_text(self):
        """
            Is this a text file?

            For systems which do not track this, a herustic is provided.
        """
        return not self.is_binary

    @property
    def text_encoding(self):
        if not self.__analysed:
            self.__file_type()
        return self.__text_encoding


    @property
    def _default_encoding(self):
        return 'UTF8'

    def __file_type(self):
        # Guess the type of a file

        self.open()
        pos = self.tell()
        self.seek(0)
        dat = self.read(1024)

        if dat.startswith('\xFE\xFF'):
            self.__is_binary     = False
            self.__text_encoding = 'UTF16-BE'

        elif dat.startswith('\xFF\xFE'):
            self.__is_binary     = False
            self.__text_encoding = 'UTF16-LE'

        elif dat.startswith('\xEF\xBB\xBF'):
            self.__is_binary     = False
            self.__text_encoding = 'UTF8'

        elif '\x00' in dat:
            self.__is_binary     = True

        else:
            # Text of some unknown form
            self.__is_binary     = False
            self.__text_encoding = self._default_encoding

        self.seek(pos)
        self.__analysed = True

    def open(self):
        """
            Opens the file for reading. This must be invoked before using any
            of the file methods, in order to permit plugins to do lazy
            initialization.

            There must be no side effects if open is called a multiple times.
        """
        pass