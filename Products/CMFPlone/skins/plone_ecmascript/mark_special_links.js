/* Scan all links in the document and set classes on them if
 * mark external links is turned on and
 * they point outside the site, or are special protocols.
 * Also implements new window opening for external links.
 * To disable this effect for links on a one-by-one-basis,
 * give them a class of 'link-plain'
 */

/*
    Provides global scanforlinks
*/

/*global external_links_open_new_window, mark_special_links */

function scanforlinks() {
    // first make external links open in a new window, afterwards do the
    // normal plone link wrapping in only the content area
    var elonw,
        mslinks,
        url,
        protocols,
        contentarea,
        res;

    if (typeof external_links_open_new_window === 'string') {
        elonw = external_links_open_new_window.toLowerCase() === 'true';
    } else {
        elonw = false;
    }

    if (typeof mark_special_links === 'string') {
        mslinks = mark_special_links.toLowerCase() === 'true';
    } else {mslinks = false;}

    url = window.location.protocol + '//' + window.location.host;

    if (elonw) {
        // all http links (without the link-plain class), not within this site
        jQuery('a[href^=http]:not(.link-plain):not([href^=' + url + '])')
            .attr('target', '_blank');
    }

    if (mslinks) {
      protocols = /^(mailto|ftp|news|irc|h323|sip|callto|https|feed|webcal)/;
      contentarea = jQuery('#region-content,#content');

      // All links with an http href (without the link-plain class), not within this site,
      // and no img children should be wrapped in a link-external span
      contentarea.find(
          'a[href^=http]:not(.link-plain):not([href^=' + url + ']):not(:has(img))')
          .wrap('<span></span>').parent().addClass('link-external');
      // All links without an http href (without the link-plain class), not within this site,
      // and no img children should be wrapped in a link-[protocol] span
      contentarea.find(
          'a[href]:not([href^=http]):not(.link-plain):not([href^=' + url + ']):not(:has(img))')
          .each(function() {
              // those without a http link may have another interesting protocol
              // wrap these in a link-[protocol] span
              res = protocols.exec(this.href);
              if (res) {
                  jQuery(this).wrap('<span></span>').parent().addClass('link-' + res[0]);
              }
          });
    }
}

jQuery(scanforlinks);
