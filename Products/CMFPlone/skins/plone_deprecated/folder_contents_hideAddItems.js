// function to hide the traditional add items pull down menu.

function hideTraditionalAddItemPullDown() {
    // Get the old style Add Item pulldown. We already have
    // such a menu. This is only for system that don't have javascript
    // so we can savely remove it.
    pullDown = document.getElementById('traditional-add-item-pulldown');
    if (pullDown) { 
        pullDown.style.display='none';
    }
}

registerPloneFunction(hideTraditionalAddItemPullDown)
