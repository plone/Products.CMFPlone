
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

    for (i=0; i < collapsibles.length; i++){
        if (collapsibles[i].className.indexOf('collapsible')== -1 ){
            continue
            }
        legends = collapsibles[i].getElementsByTagName('LEGEND')
        /*
         * get the legend
         * if there is no legend, we do not touch the fieldset at all.
         * we assume that if there is a legend, there is only one.
         * nothing else makes any sense
         */
        if (! legends.length){continue}
        legend = legends[0]

        // add the icon/button with its functionality to the legend
        icon = document.createElement('img');
        icon.setAttribute('src','treeExpanded.gif')
        icon.setAttribute('class','collapseIcon')
        icon.setAttribute('heigth','9')
        icon.setAttribute('width','9')
        icon.style.marginRight='1em';

        //set up the legend to handle click-events
        if (window.addEventListener) legend.addEventListener("click",toggleCollapsible,false);
        else if (window.attachEvent) legend.attachEvent("onclick",toggleCollapsible);
        legend.style.cursor = 'pointer';


        // insert the icon icon at the start of the legend
        legend.insertBefore(icon,legend.firstChild)
        /*
         * wrap the contents inside a div to make turning them on and off simpler.
         * unless something very strange happens, this new div should always be the last childnode
         * we'll give it a class to make sure.
         */
        hiderWrapper = document.createElement('div');
        hiderWrapper.setAttribute('class','collapseWrapper')

        // also add a new div describing that the element is collapsed.
        collapsedDescription = document.createElement('div');
        collapsedDescription.setAttribute('class','collapsedText')
        collapsedDescription.appendChild(document.createTextNode('Section is collapsed, click the [+] to expand'))
        collapsedDescription.style.display = 'none'

        // if the fieldset has the class of "collapsed", pre-collapse it. This can be used to preserve valuable UI-space
        if (collapsibles[i].className.indexOf('collapsed')!= -1 ){
            icon.setAttribute('src','treeCollapsed.gif')
            collapsedDescription.style.display = 'block'
            hiderWrapper.style.display = 'none';
            }

        // now we have the wrapper div.. Stuff all the contents inside it
        nl = collapsibles[i].childNodes.length
        for (j=0; j < nl; j++){
            node = collapsibles[i].childNodes[0]
            if ( node.nodeName == 'LEGEND'){
                if (collapsibles[i].childNodes.length > 1 ){
                    hiderWrapper.appendChild(collapsibles[i].childNodes[1])
                    }
            }else{
                hiderWrapper.appendChild(collapsibles[i].childNodes[0])
                }
            }
        // and add it to the document
        collapsibles[i].appendChild(hiderWrapper)
        collapsibles[i].insertBefore(collapsedDescription, hiderWrapper)
    }
}
registerPloneFunction(activateCollapsibles)

function toggleCollapsible(e){
    // this is the function that collapses/expands fieldsets.
    var node = window.event ? window.event.srcElement : e.currentTarget;
    // node should be the legend, but this can change later on.
    if (node.nodeName == 'IMG'){
        node = node.parentNode
        }
    var icon = node.firstChild
    var legend = node

    if( icon.getAttribute('src').indexOf('treeCollapsed.gif')!= -1 ){
        // that was an ugly check, but IE rewrites image sources to absolute urls from some sick reason....
        icon.setAttribute('src','treeExpanded.gif')
        legend.parentNode.lastChild.style.display = 'block'
        legend.parentNode.childNodes[1].style.display = 'none'
    }else{
        icon.setAttribute('src','treeCollapsed.gif')
        legend.parentNode.lastChild.style.display = 'none'
        legend.parentNode.childNodes[1].style.display = 'block'
        }
    }