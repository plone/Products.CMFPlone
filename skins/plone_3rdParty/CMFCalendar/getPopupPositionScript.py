##parameters=weeks, year, month

# weeks is a list of weeks, which are lists of days.  Days are dictionaries.
# This script should return a body of javascript text for the positions of the
# popup boxes that you get when you hold the cursor over the calender.

#document.getElementById('day%d%0.2d%0.2d').style.top + 
#document.getElementById('day%d%0.2d%0.2d').style.left + 

jstext = """
      function findPosX(obj)
      {
        var curleft = 0;
        if (document.getElementById || document.all)
        {
          while (obj.offsetParent)
          {
            curleft += obj.offsetLeft
            obj = obj.offsetParent;
          }
        }
        else if (document.layers)
          curleft += obj.x;
        return curleft;
      }

      function findPosY(obj)
      {
        var curtop = 0;
        if (document.getElementById || document.all)
        {
          while (obj.offsetParent)
          {
            curtop += obj.offsetTop
            obj = obj.offsetParent;
          }
        }
        else if (document.layers)
          curtop += obj.y;
        return curtop;
      }

function setpositions() {
  var calposY = findPosY(document.getElementById('thecalendar'));
  var calposX = findPosX(document.getElementById('thecalendar'));

//alert (calposX + ", " + calposY);"""
jstemplate = """document.getElementById('day%d%0.2d%0.2d').style.pixelTop = %d + calposY; // + "em";
document.getElementById('day%d%0.2d%0.2d').style.pixelLeft = %d + calposX; // + "em";
alert (document.getElementById('day%d%0.2d%0.2d').style.pixelTop + ", " + document.getElementById('day%d%0.2d%0.2d').style.pixelLeft);
"""
for weekdays in weeks:
    for day in weekdays:
        if day['event']:
            jstext = '%s\n%s' % (jstext,
                                 jstemplate % (year,
                                               month,
                                               day['day'],
                                               2 * weeks.index(weekdays) + 2,
                                               year,
                                               month,
                                               day['day'],
                                               2 * weekdays.index(day) + 3,
                                               year,
                                               month,
                                               day['day'],
                                               year,
                                               month,
                                               day['day'])
                                )
return jstext + "\n}"
