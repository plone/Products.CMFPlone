define([
  'expect',
  'jquery',
  'pat-registry',
  'mockup-patterns-markspeciallinks'
], function(expect, $, registry, MarkSpecialLinks) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

/* ==========================
   TEST: MarkSpecialLinks
  ========================== */

  describe('MarkSpecialLinks', function () {
    beforeEach(function() {
      this.$el = $ ('' +
        '<div class="pat-markspeciallinks">' +
        '  <p>Find out What&#39s new in <a href="http://www.plone.org">Plone</a>.<br>' +
        '     Plone is written in <a class="link-plain" href="http://www.python.org">Python</a>.' +
        '  </p>' +
        '</div>' +
        '<div class="pat-markspeciallinks" data-pat-markspeciallinks="external_links_open_new_window: true">' +
        '  <p>Find out What&#39s new in <a href="http://www.plone.org">Plone</a>.<br>' +
        '     Plone is written in <a class="link-plain" href="http://www.python.org">Python</a>.' +
        '  </p>' +
        '</div>' +
        '<div class="pat-markspeciallinks" data-pat-markspeciallinks="mark_special_links: false">' +
        '  <p>Find out What&#39s new in <a href="http://www.plone.org">Plone</a>.<br>' +
        '     Plone is written in <a class="link-plain" href="http://www.python.org">Python</a>.' +
        '  </p>' +
        '</div>' +
        '<div class="icons pat-markspeciallinks">' +
        '    <ul>' +
        '      <li><a href="http://www.plone.org">http</a></li>' +
        '      <li><a href="https://www.plone.org">https</a></li>' +
        '      <li><a href="mailto:info@plone.org">mailto</a></li>' +
        '      <li><a href="ftp://www.plone.org">ftp</a></li>' +
        '      <li><a href="news://www.plone.org">news</a></li>' +
        '      <li><a href="irc://www.plone.org">irc</a></li>' +
        '      <li><a href="h323://www.plone.org">h323</a></li>' +
        '      <li><a href="sip://www.plone.org">sip</a></li>' +
        '      <li><a href="callto://www.plone.org">callto</a></li>' +
        '      <li><a href="feed://www.plone.org">feed</a></li>' +
        '      <li><a href="webcal://www.plone.org">webcal</a></li>' +
        '    </ul>' +
        '</div>');


    });
    it('normal external links have target=_blank', function() {
      registry.scan(this.$el);
      var link = this.$el.find('a');
      expect(link.eq(0).attr('target')===undefined).to.be.equal(true);
      expect(link.eq(1).attr('target')===undefined).to.be.equal(true);
      expect(link.eq(2).attr('target')).to.be.equal('_blank');
      expect(link.eq(3).attr('target')===undefined).to.be.equal(true);
      expect(link.eq(0).prev()[0].tagName).to.be.equal('I');
      expect(link.eq(1).prev()[0].tagName).not.to.equal('I');
      expect(link.eq(4).prev().length).to.be.equal(0);
      expect(link.eq(5).prev()[0].tagName).not.to.equal('I');
    });
    it('check for correct icon classes per protocol', function() {
      registry.scan(this.$el);
      var listel = this.$el.next('.icons').find('li');
      expect(listel.eq(0).find('i').hasClass('link-external')).to.be.equal(true);
      expect(listel.eq(1).find('i').hasClass('link-https')).to.be.equal(true);
      expect(listel.eq(2).find('i').hasClass('link-mailto')).to.be.equal(true);
      expect(listel.eq(3).find('i').hasClass('link-ftp')).to.be.equal(true);
      expect(listel.eq(4).find('i').hasClass('link-news')).to.be.equal(true);
      expect(listel.eq(5).find('i').hasClass('link-irc')).to.be.equal(true);
      expect(listel.eq(6).find('i').hasClass('link-h323')).to.be.equal(true);
      expect(listel.eq(7).find('i').hasClass('link-sip')).to.be.equal(true);
      expect(listel.eq(8).find('i').hasClass('link-callto')).to.be.equal(true);
      expect(listel.eq(9).find('i').hasClass('link-feed')).to.be.equal(true);
      expect(listel.eq(10).find('i').hasClass('link-webcal')).to.be.equal(true);
    });
  });
});
