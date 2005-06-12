
function activateMenu(event, menu_id) {
    if (!event) var event = window.event; // IE compatibility

    // terminate if we hit a non-compliant DOM implementation
    // returning true, so the link is still followed
    if (! document.getElementsByTagName){return true;}
    if (! document.getElementById){return true;}

    menu = document.getElementById(menu_id);

    if (menu.style.display == 'block')
        menu.style.display = 'none';
    else
        menu.style.display = 'block';

    return false;
}
