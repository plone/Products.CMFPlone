
function setDisplayMode(item, state) {
// change the display prop of a div to none/block if the div exists
    if (document.getElementById(item) != null) {
        document.getElementById(item).style.display = state;
    }
}
function toggleFullScreenMode() {
    // toggle the display prop of the columns    
    if (document.getElementById('portal-column-one').style.display == 'none') {
        try {
            setDisplayMode('portal-logo', 'block');
            setDisplayMode('portal-siteactions', 'block');
            setDisplayMode('portal-column-one', 'table-cell');
            setDisplayMode('portal-column-two', 'table-cell');
        } catch (e) {
            // silly IE does not understand display:table-cell, so we must workaround
            // alert(e);
            if (e == "[object Error]") {
                setDisplayMode('portal-logo', 'block');
                setDisplayMode('portal-siteactions', 'block');
                setDisplayMode('portal-column-one', 'block');
                setDisplayMode('portal-column-two', 'block');
            } else {
                throw e;
            }
        }
        // set cookie
        createCookie('fullscreenMode', '');
    } else {
        setDisplayMode('portal-logo', 'none');
        setDisplayMode('portal-siteactions', 'none');
        setDisplayMode('portal-column-one', 'none');
        setDisplayMode('portal-column-two', 'none');
        createCookie('fullscreenMode', '1');
    }
}

function fullscreenModeLoad() {
// based on cookie hide div
        if (readCookie('fullscreenMode') == '1') {        
        setDisplayMode('portal-logo', 'none');
        setDisplayMode('portal-siteactions', 'none');
        setDisplayMode('portal-column-one', 'none');
        setDisplayMode('portal-column-two', 'none');    
        }
}
registerPloneFunction(fullscreenModeLoad)