x = XMLRPC;

function GetPreview(text, element) {
    var url = portal_url;
    var script = "formatStx";

    res = x.call(url, script, text);
    elm = document.getElementById(element);
    elm.innerHTML = res;
}
