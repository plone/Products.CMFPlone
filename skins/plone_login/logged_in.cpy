## Script (Python) "logged_in"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Initial post-login actions
##
from DateTime import DateTime
import ZTUtils

REQUEST=context.REQUEST

# If someone has something on their clipboard, expire it.
if REQUEST.get('__cp', None) is not None:
    REQUEST.RESPONSE.expireCookie('__cp', path='/')

membership_tool=context.portal_membership
if membership_tool.isAnonymousUser():
    REQUEST.RESPONSE.expireCookie('__ac', path='/')
    return state.set(status='failure', portal_status_message='Login failed')

member = membership_tool.getAuthenticatedMember()
login_time = member.getProperty('login_time', context.ZopeTime())
if  str(login_time) == '2000/01/01':
    state.set(status='initial_login')
member.setProperties(last_login_time = login_time,
                     login_time = context.ZopeTime())

if hasattr(membership_tool, 'createMemberArea'):
    # This is acutally a capablities test.  For non-mgmt users, the
    # hasattr test above test will fail under CMF 1.4 but will succeed
    # under CMF HEAD due do security machinery magic.  Hasattr will
    # return false under CMF 1.4 because the createMemberArea method
    # is protected by 'Manage portal' permission.  Under CMF HEAD+,
    # createMemberArea is declared public, so it will succeed.

    # This is necessary because in CMF 1.4, the wrapUser method
    # creates a member folder automatically.  However under the HEAD,
    # it is this script's responsibility to do so.  So we only want to
    # call createMemberArea under CMF HEAD+.

    membership_tool.createMemberArea()

return state
