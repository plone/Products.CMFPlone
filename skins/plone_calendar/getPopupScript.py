##parameters=inputname,formname

return r"""

function returndate(day)
{
  opener.document.%(formname)s.%(inputname)s.value = day
  window.close()
}
""" % {'inputname':inputname, 'formname':formname}
