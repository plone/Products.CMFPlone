<%
	strJumpTo = ""
	strQueryString = Request.QueryString
	If Left(strQueryString, 7) = "JumpTo=" Then
		strJumpTo = Right(strQueryString, Len(strQueryString) - 7)
		strQueryString = ""
	End If
%>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">

<html>
<head>
	<title>Status Redirect</title>
</head>
<script language="javascript">
	function Redir()
		{
			opener.document.location="<%= strJumpTo & strQueryString %>";
			opener.focus();
			window.close();
		}
</script>
<body onload="Redir();">



</body>
</html>
