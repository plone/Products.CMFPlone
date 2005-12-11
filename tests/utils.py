import transaction
from Testing.ZopeTestCase.utils import appcall

def setupBrowserIdManager(app=None):
    '''Sets up the brower_id_manager.'''
    commit = 0

    if app is None: 
        return appcall(setupBrowserIdManager)

    if not hasattr(app, 'browser_id_manager'):
        from Products.Sessions.BrowserIdManager import BrowserIdManager
        bid = BrowserIdManager('browser_id_manager',
                    'Browser Id Manager')
        app._setObject('browser_id_manager', bid)
        commit = 1

    if commit:
        transaction.commit()

