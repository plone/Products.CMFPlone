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
    // first make external links open in a new window, afterwards do the
    // normal plone link wrapping in only the content area

    if (typeof external_links_open_new_window == 'string')
        var elonw = external_links_open_new_window.toLowerCase() == 'true';
    else elonw = false;

    var url = window.location.protocol + '//' + window.location.host;

    if (elonw)
        // all http links (without the link-plain class), not within this site
        jq('a[href^=http]:not(.link-plain):not([href^=' + url + '])')
            .attr('target', '_blank');

    var protocols = /^(mailto|ftp|news|irc|h323|sip|callto|https|feed|webcal)/;
    var contentarea = jq(getContentArea());

    // All links with an http href (without the link-plain class), not within this site,
    // and no img children should be wrapped in a link-external span
    contentarea.find(
        'a[href^=http]:not(.link-plain):not([href^=' + url + ']):not(:has(img))')
        .wrap('<span>').parent().addClass('link-external')
    // All links without an http href (without the link-plain class), not within this site,
    // and no img children should be wrapped in a link-[protocol] span
    contentarea.find(
        'a[href]:not([href^=http]):not(.link-plain):not([href^=' + url + ']):not(:has(img))')
        .each(function() {
            // those without a http link may have another interesting protocol
            // wrap these in a link-[protocol] span
            if (res = protocols.exec(this.href))
                jq(this).wrap('<span>').parent().addClass('link-', res[0]);
        });
};
jq(scanforlinks);
