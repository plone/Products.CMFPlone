##parameters=weeks, year, month
csstext=""
csstemplate = """
#day%d%0.2d%0.2d {
  position: absolute;
  visibility: hidden;
}"""
for weekdays in weeks:
    for day in weekdays:
        if day['event']:
            csstext += csstemplate % (year,
                                     month,
                                     day['day']
                                     )
return csstext
