# -*- coding: utf-8 -*-
from datetime import datetime
from plone.resource.directory import FilesystemResourceDirectory
from plone.resource.file import FilesystemFile
from Products.CMFCore.FSFile import FSFile
from Products.Five.browser.resource import DirectoryResource
from Products.Five.browser.resource import FileResource
from zExceptions import NotFound
from zope.component.hooks import getSite

import os


class Bundle(object):
    """Wraps pure bundles RecordsProxy and enrich with logic
    .
    Proxy attributes and provide some utility functions
    """

    def __init__(self, data):
        """initialize Bunde.initialize

        data is a
        - registry record
        - with interfaces'IResourceRegistry'
        - with prefix 'plone.bundles'
        """
        self.data = data

    def _real_path(self, ctx):
        if ctx == 'js':
            resource_path = self.data.jscompilation
        else:
            resource_path = self.data.csscompilation
        try:
            resource = getSite().restrictedTraverse(resource_path)
        except NotFound:
            return None, None
        if resource.__module__ == 'Products.Five.metaclass':
            try:
                return 'fs', resource.chooseContext().path
            except:
                try:
                    return 'fs', resource.context.path
                except:
                    try:
                        if callable(resource):
                            return None, None
                        else:
                            return None, None
                    except:
                        return None, None
        elif isinstance(resource, FilesystemFile):
            return 'fs', resource.path
        elif isinstance(resource, FileResource):
            return 'fs', resource.chooseContext().path
        elif isinstance(resource, DirectoryResource):
            return 'fs', resource.context.path
        elif isinstance(resource, FilesystemResourceDirectory):
            return 'fs', resource.directory
        elif isinstance(resource, FSFile):
            return 'zodb', resource._filepath
        else:
            return 'zodb', None

    @property
    def name(self):
        return self.data.__prefix__.split('/', 1)[1].rstrip('.')

    @property
    def last_compilation(self):
        """check bundles last compilation using filesystem date or date of OFS.

        if bundle has a last_compilation date newer than filesystem/OFS it wins
        always.
        """
        mods = []
        for ctx in ['js', 'css']:
            loc, path = self._real_path(ctx)
            if loc == 'fs' and os.path.exists(path):
                mods.append(datetime.fromtimestamp(os.path.getmtime(path)))
            elif loc == 'zodb':
                self.data.last_compilation
        if self.data.last_compilation and mods:
            if self.data.last_compilation > max(mods):
                return self.data.last_compilation
            else:
                return max(mods)
        return self.data.last_compilation

    @last_compilation.setter
    def last_compilation(self, value):
        self.data.last_compilation = value

    def __getattr__(self, name):
        """act as r/o wrapper"""
        return getattr(self.data, name)

    def __repr__(self):
        return '<{0}.{1} object "{2}" at {3}>'.format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.name,
            id(self)
        )
