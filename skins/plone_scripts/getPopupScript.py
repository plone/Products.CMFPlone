##parameters=input_id

return r"""

function returndate(day)
{
  opener.document.getElementById('%s').value = day;
  window.close();
}
""" % input_id
