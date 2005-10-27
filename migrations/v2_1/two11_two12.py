import string
from Products.CMFCore.utils import getToolByName

def two11_two12(portal):
    """2.1.1 -> 2.1.2
    """
    out = []

    # Remove plone_3rdParty\CMFTopic from skin layers
    removeCMFTopicSkinLayer(portal, out)

    return out


def removeCMFTopicSkinLayer(portal, out):
    """Removes plone_3rdParty\CMFTopic layer from all skins."""

    st = getToolByName(portal, 'portal_skins', None)
    if st is not None:
        old = 'plone_3rdParty/CMFTopic'
        skins = st.getSkinSelections()
        for skin in skins:
            path = st.getSkinPath(skin)
            path = map(string.strip, string.split(path,','))
            if old in path:
                path.remove(old)
            st.addSkinSelection(skin, ','.join(path))
        out.append("Removed plone_3rdParty\CMFTopic layer from all skins.")

