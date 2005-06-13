function activateCollapsibles(){
    /*
     * a script that searches for sections that can be (or are already) collapsed
     * - and enables the collapse-behavior

     * usage : give the class "collapsible" to a fieldset
     * also , give it a <legend> with some descriptive text.
     * you can also add the class "collapsed" amounting to a total of <fieldset class="collapsible collapsed">
     * to make the section pre-collapsed
     */

    // terminate if we hit a non-compliant DOM implementation
    if (! document.getElementsByTagName){return false};
    if (! document.getElementById){return false};

    // only search in the content-area
    contentarea = getContentArea()
    if (! contentarea){return false}

    // gather all objects that are to be collapsed
    // we only do fieldsets for now. perhaps DIVs later is it is needed...
    collapsibles = contentarea.getElementsByTagName('fieldset');

    for (i=0; i < collapsibles.length; i++) {
        if (collapsibles[i].className.indexOf('collapsible')== -1 ) {
            continue;
        }
        
        fieldset = collapsibles[i]
        legends = fieldset.getElementsByTagName('LEGEND')
        /*
         * get the legend
         * if there is no legend, we do not touch the fieldset at all.
         * we assume that if there is a legend, there is only one.
         * nothing else makes any sense
         */
        if (! legends.length) {
            continue;
        }
        legend = legends[0]

        // add the icon/button with its functionality to the legend
        icon = document.createElement('img');
        icon.setAttribute('src','treeExpanded.gif')
        icon.setAttribute('class','collapseIcon')
        icon.setAttribute('height','9')
        icon.setAttribute('width','9')

        
        // insert the icon icon at the start of the legend
        legend.insertBefore(icon,legend.firstChild)

        /*
         * create a DOM fragment to represent the collapsed fieldset
         * it's a div + span, very similar to fieldset + legend, but I couldn't
         * make fieldset collapse to a single line no matter what I tried. -- NeilK.
         */
        
        cFieldset = document.createElement('div');
        cFieldset.setAttribute('class','collapsedFieldset');
        
        cLegend = document.createElement('span');
        cLegend.setAttribute('class', 'collapsedLegend');
        var legendChildren = legend.childNodes;
        for (i = 0; i < legendChildren.length; i++) {
            elm = legendChildren[i].cloneNode(true);
            if (i == 0 && i.nodeName == 'IMG') { // it's the icon
                elm.setAttribute('src','treeCollapsed.gif');
            }    
            cLegend.appendChild(elm);
        }
        
        cFieldset.appendChild(cLegend)
     
        new Collapsible();  // hack for some old browsers to wake it up.
        c = new Collapsible(fieldset, cFieldset, legend, cLegend);
        c.init();
    }
}
    
registerPloneFunction(activateCollapsibles)

function addHandler(target,eventName,obj,handlerName) { 
    fn = function(e){obj[handlerName](e)};
    if ( window.addEventListener ) { 
         target.addEventListener(eventName, fn, false);
    } else if ( window.attachEvent ) { 
         target.attachEvent("on" + eventName, fn);
    } 
}


// defines two nodes that are siblings, clicking on one hides itself
// and reveals the other.
function Collapsible(expanded, collapsed, collapseButton, expandButton) {
    this.expanded = expanded;
    this.collapsed = collapsed;
    this.expandButton = expandButton;
    this.collapseButton = collapseButton;
}



Collapsible.prototype.init = function() {
    
    // add handlers to collapse/expand. 
    addHandler(this.collapseButton, "click", this, "collapse")
    addHandler(this.expandButton, "click", this, "expand")
    
//    addListener(this.collapseButton, closure(this.collapse) );
//  addListener(this.expandButton, closure(this.expand) );
    
    /* by default, show expanded, 
     * unless expanded class name also has 
     * 'collapsed' in it, i.e. <fieldset class="collapsible collapsed">
     */
    if (this.expanded.className.indexOf('collapsed') == -1 ) {
        this.collapse();
    } else {
        this.expand();
    }
+
    // assumption: expanded is already in document, has parent node.
    this.expanded.parentNode.insertBefore( this.collapsed, this.expanded );
}

Collapsible.prototype.collapse = function() {
    this.expanded.style.display = 'none';
    this.collapsed.style.display = 'block';
}    

Collapsible.prototype.expand = function() {
    this.expanded.style.display = 'block';
    this.collapsed.style.display = 'none';
}    
