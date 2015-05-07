from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
import httplib
from Products.CMFPlone.interfaces import ITinyMCESchema
from Products.CMFPlone.interfaces.atd import IATDProxyView
from zope.interface import implements


class ATDProxyView(object):
    """ Proxy for the 'After the Deadline' spellchecker
    """
    implements(IATDProxyView)

    def checkDocument(self):
        """ Proxy for the AtD service's checkDocument function
            See http://www.afterthedeadline.com/api.slp for more info.
        """
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ITinyMCESchema, prefix="plone", check=False)
        if settings.libraries_spellchecker_choice != 'AtD':
            return 'atd not enabled'

        tool = getToolByName(self.context, "portal_membership")
        if bool(tool.isAnonymousUser()):
            return 'must be authenticated to use atd'

        data = self.request._file.read()
        service_url = settings.libraries_atd_service_url
        service = httplib.HTTPConnection(service_url)
        service.request("POST", "/checkDocument", data)

        response = service.getresponse()

        if response.status != httplib.OK:
            service.close()
            raise Exception('Unexpected response code from AtD service %d' %
                            response.status)

        self.request.RESPONSE.setHeader('content-type',
                                        'text/xml;charset=utf-8')
        respxml = response.read()
        service.close()
        xml = respxml.strip().replace("\r", '').replace("\n", '').replace(
            '>  ', '>')
        return xml