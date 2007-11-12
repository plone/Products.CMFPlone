/* Scan all links in the document and set classes on them if
 * they point outside the site, or are special protocols
 * To disable this effect for links on a one-by-one-basis,
 * give them a class of 'link-plain'
 *
 * NOTE: This script is no longer hooked up, since we use CSS to do this now.
 *       (see public.css for the implementation)
 *       It's not removed from existing sites that use it, but new sites will
 *       not have it enabled. The CSS approach works in all modern browsers,
 *       but not Internet Explorer 6. It works fine in IE7, however.
 */

function scanforlinks() {
    // terminate if we hit a non-compliant DOM implementation
    if (!W3CDOM) { return false; }

    // first make external links open in a new window, afterwards do the
    // normal plone link wrapping in only the content area

    if (typeof external_links_open_new_window == 'string') {
        if (external_links_open_new_window.toLowerCase() == 'true') {
             external_links_open_new_window = Boolean(true)
         } else {
             external_links_open_new_window = Boolean(false)
         }
    }

    var this_site = window.location.protocol
                    + '//'
                    + window.location.host;
    var links;

    if ((typeof external_links_open_new_window != 'undefined') &&
        (external_links_open_new_window == true)) {
        links = document.getElementsByTagName('a');
        for (i=0; i < links.length; i++) {
            if ( (links[i].getAttribute('href'))
                 && (links[i].className.indexOf('link-plain')==-1) ) {
                var linkval = links[i].getAttribute('href');

                // check if the link href is a relative link, or an absolute link to
                // the current host.
                if (linkval.toLowerCase().indexOf(this_site)==0) {
                    // absolute link internal to our host - do nothing
                } else if (linkval.indexOf('http:') != 0) {
                    // not a http-link. Possibly an internal relative link, but also
                    // possibly a mailto or other protocol add tests for relevant
                    // protocols as you like.
                    // do nothing
                } else {
                    // we are in here if the link points to somewhere else than our
                    // site.
                    // set external_links_open_new_window in Site setup / Theme
                    // to true if you want external links to be opened in a new
                    // window.
                    links[i].setAttribute('target', '_blank');
                }
            }
        }
    }

    var contentarea = getContentArea();
    if (!contentarea)
        return false;

    var protocols = ['mailto', 'ftp', 'news', 'irc', 'h323', 'sip',
                     'callto', 'https', 'feed', 'webcal'];

    links = contentarea.getElementsByTagName('a');
    for (i=0; i < links.length; i++) {
        if ( (links[i].getAttribute('href'))
             && (links[i].className.indexOf('link-plain')==-1) ) {
            var linkval = links[i].getAttribute('href');

            // check if the link href is a relative link, or an absolute link to
            // the current host.
            if (linkval.toLowerCase().indexOf(this_site)==0) {
                // absolute link internal to our host - do nothing
            } else if (linkval.indexOf('http:') != 0) {
                // not a http-link. Possibly an internal relative link, but also
                // possibly a mailto or other protocol add tests for relevant
                // protocols as you like.
                // h323, sip and callto are internet telephony VoIP protocols
                for (p=0; p < protocols.length; p++) {
                    if (linkval.indexOf(protocols[p]+':') == 0) {
                        // if the link matches one of the listed protocols, add
                        // className = link-protocol
                        wrapNode(links[i], 'span', 'link-'+protocols[p]);
                        break;
                    }
                }
            } else {
                // we are in here if the link points to somewhere else than our
                // site.
                if ( links[i].getElementsByTagName('img').length == 0 ) {
                    // we do not want to mess with those links that already have
                    // images in them
                    wrapNode(links[i], 'span', 'link-external');
                }
            }
        }
    }
};

registerPloneFunction(scanforlinks);
