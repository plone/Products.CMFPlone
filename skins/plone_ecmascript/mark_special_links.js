
// script for detecting external links.
// sets their target-attribute to _blank , and adds a class external

function scanforlinks(){
    // securing against really old DOMs 
    
    if (! document.getElementsByTagName){return false};
    if (! document.getElementById){return false};
    // Quick utility function by Geir Bækholt
    // Scan all links in the document and set classes on them dependant on 
    // whether they point to the current site or are external links
    
    contentarea = getContentArea()
    if (! contentarea){return false}
    
    links = contentarea.getElementsByTagName('a');
    for (i=0; i < links.length; i++){      
        if ((links[i].getAttribute('href'))&&(links[i].className.indexOf('link-plain')==-1 )){
            var linkval = links[i].getAttribute('href')
            // check if the link href is a relative link, or an absolute link to the current host.
			if (linkval.toLowerCase().indexOf(window.location.protocol+'//'+window.location.host)==0) {
                // we are here because the link is an absolute pointer internal to our host
                // do nothing
            } else if (linkval.indexOf('http:') != 0){
                // not a http-link. Possibly an internal relative link, but also possibly a mailto ot other snacks
                // add tests for all relevant protocols as you like.
                
                protocols = ['mailto', 'ftp', 'news', 'irc', 'h323', 'sip', 'callto', 'https']
                // h323, sip and callto are internet telephony VoIP protocols
                
                for (p=0; p < protocols.length; p++){  
                     if (linkval.indexOf(protocols[p]+':') == 0){
                    // this link matches the protocol . add a classname protocol+link
                    //links[i].className = 'link-'+protocols[p]
                        wrapNode(links[i], 'span', 'link-'+protocols[p])
                        break;
                    }
                }
            }else{
                // we are in here if the link points to somewhere else than our site.
                if ( links[i].getElementsByTagName('img').length == 0 ){
					// we do not want to mess with those links that already have images in them
                    //links[i].className = 'link-external'
                    wrapNode(links[i], 'span', 'link-external')
                    //links[i].setAttribute('target','_blank')
                    }
                
                
                
                
            }
        }
    }
}
registerPloneFunction(scanforlinks)   

