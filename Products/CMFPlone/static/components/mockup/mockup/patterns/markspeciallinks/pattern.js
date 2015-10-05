/* Mark special links
 *
 * Options:
 *    external_links_open_new_window(boolean): Open external links in a new window. (false)
 *    mark_special_links(boolean): Marks external or special protocl links with class. (true)
 *
 * Documentation:
 *   # General
 *
 *   Scan all links in the container and mark external links with class
 *   if they point outside the site, or are special protocols.
 *   Also implements new window opening for external links.
 *   To disable this effect for links on a one-by-one-basis,
 *   give them a class of 'link-plain'
 *
 *   # Default external link example
 *
 *   {{ example-1 }}
 *
 *   # Open external link in new window
 *
 *   {{ example-2 }}
 *
 *   # Open external link in new window, without icons
 *
 *   {{ example-3 }}
 *
 *   # List of all protocol icons
 *
 *   {{ example-4 }}
 *
 * Example: example-1
 *    <div class="pat-markspeciallinks">
 *      <ul>
 *        <li>Find out What's new in <a href="http://www.plone.org">Plone</a>.</li>
 *        <li>Plone is written in <a class="link-plain" href="http://www.python.org">Python</a>.</li>
 *        <li>Plone builds on <a href="http://zope.org">Zope</a>.</li>
 *        <li>Plone uses <a href="/">Mockup</a>.</li>
 *      </ul>
 *    </div>
 *
 * Example: example-2
 *    <div class="pat-markspeciallinks" data-pat-markspeciallinks='{"external_links_open_new_window": "true"}'>
 *      <ul>
 *        <li>Find out What's new in <a href="http://www.plone.org">Plone</a>.</li>
 *        <li>Plone is written in <a class="link-plain" href="http://www.python.org">Python</a>.</li>
 *        <li>Plone builds on <a href="http://zope.org">Zope</a>.</li>
 *        <li>Plone uses <a href="/">Mockup</a>.</li>
 *      </ul>
 *    </div>
 *
 * Example: example-3
 *    <div class="pat-markspeciallinks" data-pat-markspeciallinks='{"external_links_open_new_window": "true", "mark_special_links": "false"}'>
 *      <ul>
 *        <li>Find out What's new in <a href="http://www.plone.org">Plone</a>.</li>
 *        <li>Plone is written in <a class="link-plain" href="http://www.python.org">Python</a>.</li>
 *        <li>Plone builds on <a href="http://zope.org">Zope</a>.</li>
 *        <li>Plone uses <a href="/">Mockup</a>.</li>
 *      </ul>
 *    </div>
 *
 * Example: example-4
 *    <div class="pat-markspeciallinks">
 *        <ul>
 *          <li><a href="http://www.plone.org">http</a></li>
 *          <li><a href="https://www.plone.org">https</a></li>
 *          <li><a href="mailto:info@plone.org">mailto</a></li>
 *          <li><a href="ftp://www.plone.org">ftp</a></li>
 *          <li><a href="news://www.plone.org">news</a></li>
 *          <li><a href="irc://www.plone.org">irc</a></li>
 *          <li><a href="h323://www.plone.org">h323</a></li>
 *          <li><a href="sip://www.plone.org">sip</a></li>
 *          <li><a href="callto://www.plone.org">callto</a></li>
 *          <li><a href="feed://www.plone.org">feed</a></li>
 *          <li><a href="webcal://www.plone.org">webcal</a></li>
 *        </ul>
 *    </div>
 *
 */

define([
  'mockup-patterns-base',
  'jquery'
], function (Base, $) {
  'use strict';

  var MarkSpecialLinks = Base.extend({
    name: 'markspeciallinks',
    trigger: '.pat-markspeciallinks',
    defaults: {
      external_links_open_new_window: false,
      mark_special_links: true
    },
    init: function () {
      var self = this, $el = self.$el;

      // first make external links open in a new window, afterwards do the
      // normal plone link wrapping in only the content area
      var elonw,
          msl,
          url,
          protocols,
          contentarea,
          res;

      if (typeof self.options.external_links_open_new_window === 'string') {
          elonw = self.options.external_links_open_new_window.toLowerCase() === 'true';
      } else if (typeof self.options.external_links_open_new_window === 'boolean') {
          elonw = self.options.external_links_open_new_window;
      }

      if (typeof self.options.mark_special_links === 'string') {
          msl = self.options.mark_special_links.toLowerCase() === 'true';
      } else if (typeof self.options.mark_special_links === 'boolean') {
          msl = self.options.mark_special_links;
      }

      url = window.location.protocol + '//' + window.location.host;
      protocols = /^(mailto|ftp|news|irc|h323|sip|callto|https|feed|webcal)/;
      contentarea = $el;

      if (elonw) {
          // all http links (without the link-plain class), not within this site
          contentarea.find('a[href^="http"]:not(.link-plain):not([href^="' + url + '"])')
                     .attr('target', '_blank');
      }

      if (msl) {
        // All links with an http href (without the link-plain class), not within this site,
        // and no img children should be wrapped in a link-external span
        contentarea.find(
            'a[href^="http:"]:not(.link-plain):not([href^="' + url + '"]):not(:has(img))')
            .before('<i class="glyphicon link-external"></i>');
        // All links without an http href (without the link-plain class), not within this site,
        // and no img children should be wrapped in a link-[protocol] span
        contentarea.find(
            'a[href]:not([href^="http:"]):not(.link-plain):not([href^="' + url + '"]):not(:has(img))')
            .each(function() {
                // those without a http link may have another interesting protocol
                // wrap these in a link-[protocol] span
                res = protocols.exec(this.href);
                if (res) {
                    var iconclass = 'glyphicon link-' + res[0];
                    $(this).before('<i class="' + iconclass + '"></i>');
                }
            }
        );
      }
    }
  });
  return MarkSpecialLinks;
});
