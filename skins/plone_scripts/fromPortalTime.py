## Script (Python) "fromPortalTime"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=time=None, long_format=None
##title=
##
#given a time string convert it into a DateTime and then format it appropariately
#Written by Sigve Tjora, http://www.tjora.no
#To be sucessfull the format must include at least %Y or %y, %m and %d. Only names for
#month will not work.

from DateTime import DateTime

time=time.strip()
properties=context.portal_properties.site_properties
longformat=properties.localLongTimeFormat
shortformat=properties.localTimeFormat

if time is None: 
    return DateTime() #If no time, return now
t_dict={} #dict to hold tokenes

def checkTimeString(time, format):
    try:
        formatnr=0
        inputnr=0
        t_dict={}
        while formatnr<len(format):
            if longformat[formatnr]=="%":
                token=format[formatnr+1]
                formatnr=formatnr+2
                start=inputnr
                if token=="p":
                    try:
                        p=time[inputnr:inputnr+2].lower()
                        inputnr=inputnr+2
                        if not(p=="pm" or p=="am"):
                            t_dict={}
                            break
                        else:
                            t_dict[token]=p
                    except:
                        t_dict={}
                        break                    
                else:
                    try: #find end...
                        while 1:
                            a=int(time[inputnr])
                            inputnr=inputnr+1
                    except:
                        t_dict[token]=int(time[start:inputnr])
            else:
                if not (len(time)>inputnr and time[inputnr]==format[formatnr]):
                    t_dict={}
                    break
                inputnr=inputnr+1
                formatnr=formatnr+1
        return t_dict
    except:
        return {}

t_dict=checkTimeString(time, longformat)    

if not t_dict:
    t_dict=checkTimeString(time, shortformat)

#Construct date time out of how much information we have got.    
if t_dict.has_key('p') and t_dict.has_key('I'):
    if t_dict['p'].lower()=='pm':
        t_dict['H']=int(t_dict['I'])+12
    else:
        t_dict['H']=t_dict['I']
if t_dict.has_key('d') and t_dict.has_key('m') and (t_dict.has_key('y') or t_dict.has_key('Y')):
    if t_dict.has_key('Y'):
        year=int(t_dict['Y'])
    else:
        year=int(t_dict['y'])
    month=int(t_dict['m'])
    day=int(t_dict['d'])
    
    if t_dict.has_key('M') and t_dict.has_key('H'):
        min=int(t_dict['M'])
        hour=int(t_dict['H'])
        if t_dict.has_key('S'):
            sec=int(t_dict['S'])
            return DateTime(year, month, day, hour, min, sec)
        else:
            return DateTime(year, month, day, hour, min)
    else:
        return DateTime(year, month, day)
else:
    #We didn't get enough data out, let DateTime try.
    return DateTime(time)

