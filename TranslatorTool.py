from Products.CMFCore.utils import UniqueObject
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

class TranslatorTool (UniqueObject, SimpleItem):
    """ encapsulates the ways forms should and can work inside a CMF """
    id = 'portal_translator'
    meta_type= 'CMF ZBabel Tool'
    security = ClassSecurityInfo()
    plone_tool = 1
    
    def _match_lang(self, spec, lang):
	if spec == lang or lang[:len(spec)] == spec:
	    return lang
    
    security.declareObjectPublic()
    security.declarePublic('__call__')
    def __call__(self, label):
	tower_id = getattr(self, 'tower_id', 'ZBabelTower')
	tower = getattr(self, tower_id, None)
	if tower is None:
	    return label
	lang_list = []
	if not getattr(self, 'ignore_accept_language', 0):
	    req = getattr(self, 'REQUEST', None)
	    if req:
		lang_list = req.get('HTTP_ACCEPT_LANGUAGE', '').split(',')
		# FIXME: sort by quality?
		# browsers that don't send the list already sorted should be shot on sight.
		lang_list = [l.split(';')[0].strip() for l in lang_list]
	default = getattr(self, 'portal_default_language', None)
	if default:
	    lang_list.append(default)
	tower_langs = tower.getAllLanguages()
	# ZBabelTower doesn't support language names with hyphens
	lang_list = [l.split('-') for l in lang_list]
	for lang in lang_list:
	    if len(lang) == 1:
		lang_name = lang[0]
	    else:
		lang_name = lang[0] + lang[1].upper()
	    for l in tower_langs:
		if self._match_lang(lang_name, l):
		    tr = tower.getDstPhraseFromSrcPhrase(label, l)
		    if tr:
			return tr.phrase
	# add the phrase to the tower
	# this is a bit kludgish, because we want to add just the label
	# (adding all languages would miss the point of trying the list)
	tower.addPhrase(tower._makeDigest(label), 'label', label)
	return label

InitializeClass(TranslatorTool)
