from zLOG import INFO, ERROR
from SetupBase import SetupWidget
from ConfigParser import ConfigParser

import SetupBase
import os
import glob

# Heres another bundle of joy lets read our setup directory for all the 
# possible config files

ptn = SetupBase.__file__[-9:] + "*.ini"
registeredFiles = []

def registerFile(file):
    if file not in registeredFiles:
        registeredFiles.append(file)

class LocalizerLanguageSetup(SetupWidget):
    type = 'Setup using customization files'
   
    description = """Automates the set up of other widgets so that
you dont have to manually specify all the things, but can instead
automate this."""
    
    def delItems(self, file):
        out = []
        out.append(('Not sure how to do this... retrace steps', ERROR))
        return out

    def addItems(self, file):    
        out = []
        config = ConfigParser()
        config.read(file)
        for section in config.sections():
            dct = {}
            for option in config.options(sections):
                dct[option] = config.get(section, option)

            assert dct.has_key('widget')
            w = self.migrationTool._getWidget(dct['widget'])
            w.alterItems(dct['items'].split(','))
        
        return out

    def installed(self):
        return []

    def available(self):
        return registeredFiles + [file for file in glob.glob(ptn)]
