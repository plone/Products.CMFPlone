## Script (Python) "date_components_support"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=date=None
##title=
##

from DateTime import DateTime

#id is what will show up.  December for month 12
#value is the value for the form.
#selected is whether or not it is selected

empty={'id':'----',
       'value':None,
       'selected':None}

empty_selected=empty.copy()
empty_selected['selected']=1

default=0
years=[]
days=[]
months=[]
hours=[]
minutes=[]
ampm=[]

def month_names():
    names={}
    for x in range(1,12):
        faux=DateTime('%s/1/02'%str(x))
        names[x]=faux.pMonth()
    return names

month_dict=month_names()

try:
    date=DateTime(date)
except: #XXX DateTime can throw numerous exceptions.  catch all.
    date=None

if date is None:
    date=DateTime()
    default=1
else:
    date=DateTime(date)

year=int(date.strftime('%Y'))

if default:
    years.append(empty_selected)
else:
    years.append(empty)

for x in range(year-5, year+5):
    d={'id':x,
       'value':x,
       'selected':None}
    if x==year and not default:
        d['selected']=1
    years.append(d)

month=int(date.strftime('%m'))

if default:
    months.append(empty_selected)
else:
    months.append(empty)

for x in range(1, 12):
    d={'id':x,
       'value':x,
       'selected':None}
    if x==month and not default:
        d['selected']=1
    d['id']=month_dict[x]
    months.append(d)

day=int(date.strftime('%d'))

if default:
    days.append(empty_selected)
else:
    days.append(empty)

for x in range(1,32):
    d={'id':x,
       'value':x,
       'selected':None}
    if x==day and not default:
        d['selected']=1
    days.append(d)

minute=int(date.strftime('%M'))

if default:
    minutes.append(empty_selected)
else:
    minutes.append(empty)

for x in range(0,60,5):
    d={'id':'%02d'%x,
       'value':x,
       'selected':None}
    if x==minute and not default:
        d['selected']=1
    minutes.append(d)

hour=int(date.strftime('%H'))

if default:
    hours.append(empty_selected)
else:
    hours.append(empty)

for x in range(0,24):
    d={'id':'%02d'%x,
       'value':x,
       'selected':None}
    if x==hour and not default:
        d['selected']=1
    hours.append(d)

#  ampm = date.strftime('%p');

return {'years':years, 'months':months, 'days':days,
        'hours':hours, 'minutes':minutes}

