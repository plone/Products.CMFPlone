from zLOG import INFO, ERROR
from SetupBase import SetupWidget
import Products

import os
import glob

# Utility fn's
pth = Products.__path__

def skins_path():
    skins_path = None
    for p in pth:
        skins_path = os.path.join(p, 'CMFPlone')
        if os.path.exists(skins_path):
            break
    
    if not skins_path:
        raise ValueError, "No CMFPlone found"
    
    path = ['skins', 'plone_styles']
    return os.path.join(skins_path, *path)

def skins_available():
    skins = ['default',]
    glb = os.path.join(skins_path(), '*')
    for file in glob.glob(glb):
        if os.path.isdir(file) \
            and not file.endswith('CVS'):
            skins.append(os.path.basename(file))
    
    return skins

def skins_normalizeName(skin):
    skin = skin.replace('Plone ', '')
    skin = skin.strip().lower()
    skin = skin.replace(' ', '_')
    return skin    

def skins_unNormalizeName(skin):
    skin = skin.replace('_', ' ')  
    skin = ' '.join([s.capitalize() for s in skin.split(' ')])
    skin = 'Plone %s' % skin
    return skin

def skins_pathname(skin):
    skin = skins_normalizeName(skin)
    skins_path = os.path.join(['portal_styles', skin])
    return os.path.join(skins_path)

def custom_skinLayers(skin):
    sk = list(default_skinLayers())
    sk.insert(1, skin)
    return sk

def default_skinLayers():
    CMFDefault = (
            'zpt_topic',
            'zpt_content',
            'zpt_generic',
            'zpt_control',
            'topic', 
            'content', 
            'generic', 
            'control',
            'Images'
            )
    PloneDefault = (
                    'plone_images',
                    'plone_forms',
                    'plone_scripts',
                    'plone_scripts/form_scripts',
                    'plone_styles',
                    'plone_templates',
                    'plone_3rdParty/CMFCollector',
                    'plone_3rdParty/CMFTopic',
                    'plone_3rdParty/CMFCalendar',
                    'plone_templates/ui_slots',
                    'plone_wysiwyg',
                    'plone_ecmascript'
                    )
    BasePath = ('custom',)
    return BasePath + PloneDefault + CMFDefault
    
class SkinsSetup(SetupWidget):
    type = 'Skin Setup'
   
    description = """Sets up skins for your Plone site from the filesystem"""
    
    def setup(self):
        pass
    
    def delItems(self, skins):
        out = []
        for skin in skins:           
            skin = skins_unNormalizeName(skin)
            if skin in self.installed():
                out.append(('The skin, %s is not installed' % skin, ERROR))
            out.append(('Deleting skin, %s' % skin, INFO))
            try:
                del self.portal.portal_skins.selections[skin]
            except KeyError:
                out.append(('The skin, %s is not installed' % skin, ERROR))
        return out

    def addItems(self, skins):   
        out = []
        for skin in skins:
            skin = skins_unNormalizeName(skin)
            if skin in self.installed():
                out.append(('The skin, %s is already added' % skin, ERROR))
            layers = custom_skinLayers(skin)
            skin_tool = self.portal.portal_skins
            out.append(('Adding skin, %s' % skin, INFO))
            skin_tool.addSkinSelection(skin, ','.join(layers))
        return out

    def installed(self):
        """ Use the SkinsTool API """
        skins = self.portal.portal_skins.getSkinPaths()
        s = [ skins_normalizeName(s[0]) for s in skins ]
        return s

    def available(self):
        """ Go get the skins off the filesystem """
        return skins_available()
