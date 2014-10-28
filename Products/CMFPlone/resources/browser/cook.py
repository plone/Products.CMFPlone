from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces.resources import (
    IBundleRegistry,
    IResourceRegistry,
    OVERRIDE_RESOURCE_DIRECTORY_NAME)
from slimit import minify
from cssmin import cssmin
from datetime import datetime
from plone.resource.interfaces import IResourceDirectory
from StringIO import StringIO
from zope.component.hooks import getSite
from Products.Five.browser.resource import Resource as z3_Resource
from plone.subrequest import subrequest
from Products.CMFCore.FSFile import FSFile
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo, Unauthorized
from ZPublisher.Iterators import IStreamIterator
from zope.globalrequest import getRequest, setRequest
from Acquisition import aq_base


def _removeCachingHeaders(request):
    orig_response_headers = request.RESPONSE.headers.copy()
    if_modif = request.get_header('If-Modified-Since', None)
    try:
        del request.environ['IF_MODIFIED_SINCE']
    except KeyError:
        pass
    try:
        del request.environ['HTTP_IF_MODIFIED_SINCE']
    except KeyError:
        pass
    return orig_response_headers, if_modif


def _restoreCachingHeaders(request, original_response_headers, if_modified):
    # Now restore the headers and for safety, check that we
    # have a 20x response. If not, we have a problem and
    # some browser would hang indefinitely at this point.
    assert int(request.RESPONSE.getStatus()) / 100 == 2
    request.environ['HTTP_IF_MODIFIED_SINCE'] = if_modified
    request.RESPONSE.headers = original_response_headers


def getCharsetFromContentType(contenttype, default='utf-8'):
    contenttype = contenttype.lower()
    if 'charset=' in contenttype:
        i = contenttype.index('charset=')
        charset = contenttype[i+8:]
        charset = charset.split(';')[0]
        return charset
    else:
        return default


def getResourceContent(item, context=None, request=None):
        """Fetch resource content for delivery."""
        id = item

        output = u""

        portal = getSite()

        if context is None:
            context = portal
        
        if request is None:
            request = getRequest()

        default_charset = 'utf-8'

        id = item
        # skip external resources that look like //netdna.bootstrapcdn.com/etc... 
        if id[0:2] == '//':
            return output

        # original_request = getRequest()
        # import pdb; pdb.set_trace()
        # if original_request != request:
        #     setRequest(request)

        try:
            if portal is not None:
                obj = context.restrictedTraverse(id)
            else:
                # Can't do anything other than attempt a getattr
                obj = getattr(context, id)
        except (AttributeError, KeyError):
            output += u"\n/* XXX ERROR -- could not find '%s'*/\n" % id
            content = u''
            obj = None
        except Unauthorized:
            # If we're just returning a single resource, raise an Unauthorized,
            # otherwise we're merging resources in which case just log an error
            raise

        if obj is not None:
            if isinstance(obj, z3_Resource):
                # z3 resources
                # XXX this is a temporary solution, we wrap the five resources
                # into our mechanism, where it should be the other way around.
                #
                # First thing we must be aware of: resources give a complete
                # response so first we must save the headers.
                # Especially, we must delete the If-Modified-Since, because
                # otherwise we might get a 30x response status in some cases.
                original_headers, if_modified = _removeCachingHeaders(request)
                # Now, get the content.
                try:
                    method = obj.__browser_default__(request)[1][0]
                except AttributeError: # zope.app.publisher.browser.fileresource
                    try:
                        method = obj.browserDefault(request)[1][0]
                    except (AttributeError, IndexError):
                        try:
                            method = obj.browserDefault(request)[0].__name__
                        except AttributeError:
                            # The above can all fail if request.method is
                            # POST.  We can still at least try to use the
                            # GET method, as we prefer that anyway.
                            method = getattr(obj, 'GET').__name__

                method = method in ('HEAD', 'POST') and 'GET' or method
                content = getattr(obj, method)()
                import pdb; pdb.set_trace()
                if not isinstance(content, unicode):
                    contenttype = request.RESPONSE.headers.get('content-type', '')
                    contenttype = getCharsetFromContentType(contenttype, default_charset)
                    content = unicode(content, contenttype)
                _restoreCachingHeaders(request, original_headers, if_modified)
            elif hasattr(aq_base(obj), 'meta_type') and obj.meta_type in ['DTML Method', 'Filesystem DTML Method']:
                content = obj(client=context, REQUEST=request,
                              RESPONSE=request.RESPONSE)
                contenttype = request.RESPONSE.headers.get('content-type', '')
                contenttype = getCharsetFromContentType(contenttype, default_charset)
                content = unicode(content, contenttype)
            elif hasattr(aq_base(obj), 'meta_type') and obj.meta_type == 'Filesystem File':
                obj._updateFromFS()
                content = obj._readFile(0)
                contenttype = getCharsetFromContentType(obj.content_type, default_charset)
                content = unicode(content, contenttype)
            elif hasattr(aq_base(obj), 'meta_type') and obj.meta_type in ('ATFile', 'ATBlob'):
                f = obj.getFile()
                contenttype = getCharsetFromContentType(f.getContentType(), default_charset)
                content = unicode(str(f), contenttype)
            # We should add more explicit type-matching checks
            elif hasattr(aq_base(obj), 'index_html') and callable(obj.index_html):
                original_headers, if_modified = _removeCachingHeaders(request)
                # "index_html" may use "RESPONSE.write" (e.g. for OFS.Image.Pdata)
                tmp = StringIO()
                response_write = request.RESPONSE.write
                request.RESPONSE.write = tmp.write
                try:
                    content = obj.index_html(request,
                                             request.RESPONSE)
                finally:
                    request.RESPONSE.write = response_write
                content = tmp.getvalue() or content
                if not isinstance(content, unicode):
                    content = unicode(content, default_charset)
                _restoreCachingHeaders(request, original_headers, if_modified)
            elif callable(obj):
                try:
                    content = obj(request, request.RESPONSE)
                except TypeError:
                    # Could be a view or browser resource
                    content = obj()

                if IStreamIterator.providedBy(content):
                    content = content.read()

                if not isinstance(content, unicode):
                    content = unicode(content, default_charset)
            else:
                content = str(obj)
                content = unicode(content, default_charset)

        # Add start/end notes to the resource for better
        # understanding and debugging
        if content:
            output += u'\n/* - %s - */\n' % (id,)
            output += content
            output += u'\n'

        # if original_request != request:
        #     setRequest(original_request)

        return output


def cookWhenChangingSettings(context, bundle):
    """When our settings are changed, re-cook the not compilable bundles
    """
    registry = getUtility(IRegistry)
    resources = registry.collectionOfInterface(
        IResourceRegistry, prefix="plone.resources")

    # Let's join all css and js
    css_file = ""
    js_file = ""
    # siteUrl = getSite().absolute_url()

    for package in bundle.resources:
        if package in resources:
            resource = resources[package]
            for css in resource.css:
                # css_file += getResourceContent(css)
                # css_file += '\n'
                response = subrequest(siteUrl + '/' + css, root=context)
                if response.status == 200:
                    css_file += response.getBody()
                    css_file += '\n'
                # css_obj = getSite().restrictedTraverse(css, None)
                # if css_obj:
                #     if hasattr(css_obj, 'chooseContext'):
                #         try:
                #             f = open(css_obj.chooseContext().path, 'r')
                #             css_file += f.read()
                #             css_file += '\n'
                #             f.close()
                #         except:
                #             pass
    #                 elif isinstance(css_obj, FSFile):
    #                     css_file += str(css_obj)
    #                     css_file += '\n'
    #                 elif callable(css_obj):
    #                     css_file += css_obj().encode('utf-8')
    #                     css_file += '\n'
    #                 else:
    #                     import pdb; pdb.set_trace()

            if resource.js:
                # js_file += getResourceContent(resource.js)
                response = subrequest(siteUrl + '/' + resource.js, root=context)
                if response.status == 200:
                    js_file += response.getBody()
                    js_file += '\n'

                # js_obj = getSite().restrictedTraverse(resource.js, None)
                # if js_obj:
                #     if hasattr(js_obj, 'chooseContext'):
                #         try:
                #             f = open(js_obj.chooseContext().path, 'r')
                #             js_file += f.read()
                #             js_file += '\n'
                #             f.close()
                #         except:
                #             pass
    #                 elif isinstance(js_obj, FSFile):
    #                     js_file += str(js_obj)
    #                     js_file += '\n'
    #                 elif callable(js_obj):
    #                     js_file += js_obj().encode('utf-8')
    #                     js_file += '\n'
    #                 else:
    #                     import pdb; pdb.set_trace()

    cooked_js = minify(js_file, mangle=True, mangle_toplevel=True)
    cooked_css = cssmin(css_file)

    js_path = bundle.jscompilation
    css_path = bundle.csscompilation

    # Storing js
    resource_path = js_path.split('++plone++')[-1]
    resource_name, resource_filepath = resource_path.split('/', 1)
    persistent_directory = getUtility(IResourceDirectory, name="persistent")  # noqa
    if OVERRIDE_RESOURCE_DIRECTORY_NAME not in persistent_directory:
        persistent_directory.makeDirectory(OVERRIDE_RESOURCE_DIRECTORY_NAME)  # noqa
    container = persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
    if resource_name not in container:
        container.makeDirectory(resource_name)
    folder = container[resource_name]
    fi = StringIO(cooked_js)
    folder.writeFile(resource_filepath, fi)

    # Storing css
    resource_path = css_path.split('++plone++')[-1]
    resource_name, resource_filepath = resource_path.split('/', 1)
    persistent_directory = getUtility(IResourceDirectory, name="persistent")  # noqa
    if OVERRIDE_RESOURCE_DIRECTORY_NAME not in persistent_directory:
        persistent_directory.makeDirectory(OVERRIDE_RESOURCE_DIRECTORY_NAME)  # noqa
    container = persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
    if resource_name not in container:
        container.makeDirectory(resource_name)
    folder = container[resource_name]
    fi = StringIO(cooked_css)
    folder.writeFile(resource_filepath, fi)
    bundle.last_compilation = datetime.now()

    # import transaction
    # transaction.commit()
