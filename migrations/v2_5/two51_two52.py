from Products.CMFPlone.migrations.v3_0.alphas import enableZope3Site
from Products.CMFPlone.migrations.v3_0.alphas import registerToolsAsUtilities


def two51_two52(portal):
    """2.5.1 -> 2.5.2
    """
    out = []

    # Make the portal a Zope3 site
    enableZope3Site(portal, out)

    # register some tools as utilities
    registerToolsAsUtilities(portal, out)

    # Make sure the cookie auth redirects to the correct location
    setLoginFormInCookieAuth(portal, out)

    return out


def setLoginFormInCookieAuth(portal, out):
    """Makes sure the cookie auth redirects to 'require_login' instead
       of 'login_form'."""
    uf = portal._getOb('acl_users', None)
    if uf is None or getattr(uf.aq_base, '_getOb', None) is None:
        # we have no user folder or it's not a PAS folder, do nothing
        return
    cookie_auth = uf._getOb('credentials_cookie_auth', None)
    if cookie_auth is None:
        # there's no cookie auth object, do nothing
        return
    current_login_form = cookie_auth.getProperty('login_path')
    if current_login_form != 'login_form':
        # it's customized already, do nothing
        return
    cookie_auth.manage_changeProperties(login_path='require_login')
    out.append("Changed credentials_cookie_path login_path property "
               "to 'require_login'.")
