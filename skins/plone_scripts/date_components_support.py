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
#plone_log=context.plone_log

#id is what will show up.  December for month 12
#value is the value for the form.
#selected is whether or not it is selected

empty={'id':'----', 'value':None, 'selected':None}
empty_selected={'id':'----', 'value':None, 'selected':'selected'}

default=0
years=[]
days=[]
months=[]
hours=[]
minutes=[]
ampm=[]
now=DateTime()

def month_names():
    names={}
    for x in range(1,12):
        faux=DateTime('%s/1/02'%str(x))
        names[x]=faux.pMonth()
    return names

month_dict=month_names()

#XXX This debacle is because the date that is usually passed in ends with GMT
#    and of course DateTime is too stupid to handle it.  So we strip it off.

if same_type(date, ''):
    date=date.strip()
    if not date:
        date=None
    if date and date.split(' ')[-1].startswith('GMT'):
        date=DateTime(' '.join(date.split()[:-1]))

if date is None:
    date=DateTime()
    default=1
elif not same_type(date, now):
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
    minutes.append({'id':'00','value':00,'selected':1})
else:
    minutes.append({'id':'00','value':00,'selected':None})

for x in range(5,60,5):
    d={'id':'%02d'%x,
       'value':x,
       'selected':None}
    if x==minute and not default:
        d['selected']=1
    minutes.append(d)

hour=int(date.strftime('%H'))

if default:
    hours.append({'id':'00','value':00,'selected':1})
else:
    hours.append({'id':'00','value':00,'selected':None})

for x in range(1,24):
    d={'id':'%02d'%x,
       'value':x,
       'selected':None}
    if x==hour and not default:
        d['selected']=1
    hours.append(d)

#  ampm = date.strftime('%p');

return {'years':years, 'months':months, 'days':days,
        'hours':hours, 'minutes':minutes}

