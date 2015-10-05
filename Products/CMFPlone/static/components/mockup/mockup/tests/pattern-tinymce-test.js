define([
  'expect',
  'jquery',
  'sinon',
  'pat-registry',
  'tinymce',
  'mockup-patterns-tinymce'
], function(expect, $, sinon, registry, tinymce, TinyMCE) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

  var createTinymce = function(options) {
    return registry.patterns.tinymce.init(
      $('<textarea class="pat-tinymce"></textarea>').appendTo('body'),
        options || {}
      );
  };

  describe('TinyMCE', function() {
    afterEach(function() {
      $('body').empty();
    });

    beforeEach(function() {
      this.server = sinon.fakeServer.create();
      this.server.autoRespond = true;

      this.server.respondWith('GET', /data.json/, function (xhr, id) {
        var items = [
          {
            UID: '123sdfasdf',
            getURL: 'http://localhost:8081/news/aggregator',
            path: '/news/aggregator',
            portal_type: 'Collection',
            Description: 'Site News',
            Title: 'News',
            getIcon: ''
          },
          {
            UID: 'fooasdfasdf1123asZ',
            path: '/about',
            getURL: 'http://localhost:8081/about',
            portal_type: 'Document',
            Description: 'About',
            Title: 'About',
            getIcon: 'document.png'
          },
        ];

        if (xhr.url.indexOf('123sdfasdf') !== -1) {
          // ajax request for this one val
          items.pop();
        }
        xhr.respond(200, { 'Content-Type': 'application/json' }, JSON.stringify({
          total: items.length,
          results: items
        }));
      });
    });

    it('creates tinymce', function() {
      var $el = $(
       '<div>' +
       '  <textarea class="pat-tinymce">' +
       '  </textarea>' +
       '</div>'
      ).appendTo('body');
      registry.scan($el);
      expect($el.children().length).to.be.greaterThan(1);
      tinymce.get(0).remove();
    });

    it('maintains an initial textarea value', function() {
      var $el = $(
       '<div>' +
       '  <textarea class="pat-tinymce">' +
       '    foobar' +
       '  </textarea>' +
       '</div>'
      ).appendTo('body');
      registry.scan($el);
      expect(tinymce.get(0).getContent()).to.be.equal('<p>foobar</p>');
    });

    it('loads buttons for plugins', function() {
      var $el = $(
       '<div>' +
       '  <textarea class="pat-tinymce">' +
       '  </textarea>' +
       '</div>'
      ).appendTo('body');
      registry.scan($el);
      expect(tinymce.get(0).buttons).to.have.keys('plonelink', 'ploneimage');
    });

    it('on form submit, save data to form', function() {
      var $container = $(
       '<form>' +
       '  <textarea class="pat-tinymce">' +
       '  </textarea>' +
       '</form>'
      ).appendTo('body');

      var $el = $container.find('textarea');
      var tinymce = new TinyMCE($el);
      tinymce.tiny.setContent('<p>foobar</p>');
      $container.submit(function(e) {
        e.preventDefault();
      });
      $container.trigger('submit');

      expect($el.val()).to.equal('<p>foobar</p>');
    });

    it('test create correct url from metadata', function() {
      var tiny = createTinymce({
        prependToUrl: 'resolveuid/',
        linkAttribute: 'UID'
      });
      var data = {
        UID: 'foobar'
      };
      expect(tiny.generateUrl(data)).to.equal('resolveuid/foobar');
    });
    it('test creates correct url from metadata with append', function() {
      var tiny = createTinymce({
        prependToUrl: 'resolveuid/',
        linkAttribute: 'UID',
        appendToUrl: '.html'
      });
      var data = {
        UID: 'foobar'
      };
      expect(tiny.generateUrl(data)).to.equal('resolveuid/foobar.html');
    });
    it('test parses correct attribute from url', function() {
      var tiny = createTinymce({
        prependToUrl: 'resolveuid/',
        linkAttribute: 'UID'
      });
      expect(tiny.stripGeneratedUrl('resolveuid/foobar')).to.equal('foobar');
    });

    it('test parses correct attribute from url with appended value', function() {
      var tiny = createTinymce({
        prependToUrl: 'resolveuid/',
        linkAttribute: 'UID',
        appendToUrl: '/@@view'
      });
      expect(tiny.stripGeneratedUrl('resolveuid/foobar/@@view')).to.equal('foobar');
    });

    it('test get scale from url', function() {
      var pattern = createTinymce({
        prependToScalePart: '/somescale/'
      });
      expect(pattern.getScaleFromUrl('foobar/somescale/foobar')).to.equal('foobar');
    });

    it('test get scale return null if invalid', function() {
      var pattern = createTinymce({
        prependToScalePart: '/somescale/'
      });
      expect(pattern.getScaleFromUrl('foobar')).to.equal(null);
    });

    it('get scale handles edge case of image_ for plone', function() {
      var pattern = createTinymce({
        prependToScalePart: '/somescale'
      });
      expect(pattern.getScaleFromUrl('foobar/somescale/image_large')).to.equal('large');
    });

    it('get scale with appended option', function() {
      var pattern = createTinymce({
        prependToScalePart: '/somescale/',
        appendToScalePart: '/@@view'
      });
      expect(pattern.getScaleFromUrl('foobar/somescale/large/@@view')).to.equal('large');
    });

    it('get scale handles edge case of image_ for plone', function() {
      var pattern = createTinymce({
        prependToScalePart: '/somescale'
      });
      expect(pattern.getScaleFromUrl('foobar/somescale/image_large')).to.equal('large');
    });

    it('test add link', function() {
      var pattern = createTinymce({
        prependToUrl: 'resolveuid/',
        linkAttribute: 'UID',
        relatedItems: {
          ajaxvocabulary: '/data.json'
        }
      });
      pattern.addLinkClicked();
      pattern.linkModal.linkTypes.internal.getEl().select2('data', {
        UID: 'foobar',
        portal_type: 'Document',
        Title: 'Foobar',
        path: '/foobar',
        getIcon: ''
      });
      expect(pattern.linkModal.getLinkUrl()).to.equal('resolveuid/foobar');
    });

    it('test add external link', function() {
      var pattern = createTinymce();
      pattern.addLinkClicked();
      var modal = pattern.linkModal;
      modal.linkType = 'external';
      modal.linkTypes.external.getEl().attr('value', 'http://foobar');
      expect(pattern.linkModal.getLinkUrl()).to.equal('http://foobar');
    });
    it('test add email link', function() {
      var pattern = createTinymce();
      pattern.addLinkClicked();
      pattern.linkModal.linkType = 'email';
      pattern.linkModal.linkTypes.email.getEl().attr('value', 'foo@bar.com');
      expect(pattern.linkModal.getLinkUrl()).to.equal('mailto:foo@bar.com');
    });
    it('test add image link', function() {
      var pattern = createTinymce({
        prependToUrl: 'resolveuid/',
        linkAttribute: 'UID',
        prependToScalePart: '/@@images/image/'
      });
      pattern.addImageClicked();
      pattern.imageModal.linkTypes.image.getEl().select2('data', {
        UID: 'foobar',
        portal_type: 'Document',
        Title: 'Foobar',
        path: '/foobar'
      });

      pattern.imageModal.linkType = 'image';
      pattern.imageModal.$scale.find('[value="thumb"]')[0].selected = true;
      expect(pattern.imageModal.getLinkUrl()).to.equal('resolveuid/foobar/@@images/image/thumb');
    });

    it('test adds data attributes', function() {
      var pattern = createTinymce();
      pattern.tiny.setContent('<p>blah</p>');
      pattern.addLinkClicked();
      pattern.linkModal.linkTypes.internal.getEl().select2('data', {
        UID: 'foobar',
        portal_type: 'Document',
        Title: 'Foobar',
        path: '/foobar',
        getIcon: ''
      });
      pattern.linkModal.focusElement(pattern.tiny.dom.getRoot().getElementsByTagName('p')[0]);
      pattern.linkModal.$button.trigger('click');
      expect(pattern.tiny.getContent()).to.contain('data-val="foobar"');
      expect(pattern.tiny.getContent()).to.contain('data-linktype="internal"');
    });

    it('test loading link also sets up related items correctly', function() {
      var pattern = createTinymce({
        relatedItems: {
          vocabularyUrl: '/data.json'
        }
      });

      pattern.addLinkClicked();

      pattern.linkModal.linkTypes.internal.set('123sdfasdf');
      var val = pattern.linkModal.linkTypes.internal.getEl().select2('data');
      /* XXX ajax not loading quickly enough here...
      expect(val.UID).to.equal('123sdfasdf');
      */
    });

    it('test reopen add link modal', function() {
      var pattern = createTinymce();
      pattern.addLinkClicked();
      pattern.linkModal.hide();
      expect(pattern.linkModal.modal.$modal.is(':visible')).to.equal(false);
      pattern.addLinkClicked();
      expect(pattern.linkModal.modal.$modal.is(':visible')).to.equal(true);
    });

    it('test reopen add image modal', function() {
      var pattern = createTinymce();
      pattern.addImageClicked();
      pattern.imageModal.hide();
      expect(pattern.imageModal.modal.$modal.is(':visible')).to.equal(false);
      pattern.addImageClicked();
      expect(pattern.imageModal.modal.$modal.is(':visible')).to.equal(true);
    });

    it('test loads existing link external values', function() {
      var pattern = createTinymce();

      pattern.tiny.setContent('<a href="foobar" data-linktype="external" data-val="foobar">foobar</a>');

      pattern.tiny.selection.select(pattern.tiny.dom.getRoot().getElementsByTagName('a')[0]);
      pattern.addLinkClicked();

      expect(pattern.linkModal.linkTypes.external.getEl().val()).to.equal('foobar');
    });

    it('test loads existing link email values', function() {
      var pattern = createTinymce();

      pattern.tiny.setContent('<a href="mailto:foo@bar.com" data-linktype="email" data-val="foo@bar.com">foobar</a>');

      pattern.tiny.selection.select(pattern.tiny.dom.getRoot().getElementsByTagName('a')[0]);
      pattern.addLinkClicked();

      expect(pattern.linkModal.linkTypes.email.getEl().val()).to.equal('foo@bar.com');
    });

    it('test anchor link adds existing anchors to list', function() {
      var pattern = createTinymce();

      pattern.tiny.setContent('<a class="mceItemAnchor" name="foobar"></a>');

      pattern.addLinkClicked();

      expect(pattern.linkModal.linkTypes.anchor.anchorNodes.length).to.equal(1);
    });

    it('test anchor link adds anchors from option', function() {
      var pattern = createTinymce({
        anchorSelector: 'h1'
      });

      pattern.tiny.setContent('<h1>blah</h1>');
      pattern.addLinkClicked();
      expect(pattern.linkModal.linkTypes.anchor.anchorNodes.length).to.equal(1);
    });

    it('test anchor get index', function() {
      var pattern = createTinymce({
        anchorSelector: 'h1'
      });

      pattern.tiny.setContent('<h1>blah</h1><h1>foobar</h1>');
      pattern.addLinkClicked();
      expect(pattern.linkModal.linkTypes.anchor.getIndex('foobar')).to.equal(1);
    });

    it('test anchor get url', function() {
      var pattern = createTinymce({
        anchorSelector: 'h1'
      });

      pattern.tiny.setContent('<h1>blah</h1>');
      pattern.addLinkClicked();
      pattern.linkModal.linkTypes.anchor.$select.select2('data', '0');
      expect(pattern.linkModal.linkTypes.anchor.toUrl()).to.equal('#blah');
    });

    it('test tracks link type changes', function() {
      var pattern = createTinymce({
        anchorSelector: 'h1'
      });

      pattern.addLinkClicked();
      pattern.linkModal.modal.$modal.find('.autotoc-nav a').eq(1).trigger('click');
      expect(pattern.linkModal.linkType).to.equal('upload');
    });

    it('test guess link when no data- attribute present', function() {
      var pattern = createTinymce();

      pattern.tiny.setContent('<a href="foobar">foobar</a>');

      pattern.tiny.selection.select(pattern.tiny.dom.getRoot().getElementsByTagName('a')[0]);
      pattern.addLinkClicked();

      expect(pattern.linkModal.linkTypes.external.getEl().val()).to.equal('foobar');
    });

    it('test guess anchor when no data- attribute present', function() {
      var pattern = createTinymce();

      pattern.tiny.setContent('<a href="#foobar">foobar</a><a class="mceItemAnchor" name="foobar"></a>');

      pattern.tiny.selection.select(pattern.tiny.dom.getRoot().getElementsByTagName('a')[0]);
      pattern.addLinkClicked();

      expect(pattern.linkModal.linkTypes.anchor.toUrl()).to.equal('#foobar');
    });

    it('test inline tinyMCE roundtrip', function() {
      var $container = $(
       '<form>' +
       '<textarea class="pat-tinymce" data-pat-tinymce=\'{"inline": true}\'>' +
       '<h1>just testing</h1>' +
       '</textarea>' +
       '</form>'
      ).appendTo('body');
      registry.scan($container);

      var $el = $container.find('textarea');
      var id = $el.attr('id');

      var $editable = $container.find('#' + id + '-editable');

      // check, if everything is in place
      expect($editable.is('div')).to.be.equal(true);
      expect($editable.html()).to.be.equal($el.val());

      // check, if changes are submitted on form submit
      var changed_txt = 'changed contents';
      $editable.html(changed_txt);
      var $form = $container.find('form');
      $container.trigger('submit');
      expect($el.val()).to.be.equal(changed_txt);
    });

  });

});
