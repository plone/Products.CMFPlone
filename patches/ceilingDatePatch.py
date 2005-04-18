from DateTime import DateTime

APPLY_CEILING_DATE_PATCH = True     # Set to False for CMF 1.5

# This is the new ceiling date
CEILING_DATE = DateTime(2500, 0)    # 2499/12/31


# Fixup the ceiling date in CMF 1.4 DublinCore
#
if APPLY_CEILING_DATE_PATCH:
    from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
    DefaultDublinCoreImpl._DefaultDublinCoreImpl__CEILING_DATE = CEILING_DATE
