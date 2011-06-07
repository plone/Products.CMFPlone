##parameters=input_id
from zExceptions import Forbidden
if container.REQUEST.get('PUBLISHED') is script:
   raise Forbidden('Script may not be published.')


return r"""

function returndate(day)
{
  opener.document.getElementById('%s').value = day;
  window.close();
}
""" % input_id
