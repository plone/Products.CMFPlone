## Script (Python) "aCustom.py"
##parameters=thetime
##title=Given a DateTime object, return a slightly more compact aCommon repr.

if same_type(thetime, ""):
    import DateTime
    dt = DateTime.DateTime(thetime)
else:
    dt = thetime

return "%s %s, %s %s" % (dt.aMonth(), dt.day(), dt.yy(), dt.TimeMinutes())

