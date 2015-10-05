define([
  'expect',
  'jquery',
  'mockup-utils'
], function(expect, $, utils) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

  describe('utils', function () {

    describe('setId', function() {

      it('by default uses "id" as prefix', function() {
        var $el = $('<div>'),
            id = utils.setId($el);
        expect(id).to.not.be.an('undefined');
        expect(id).to.be.a('string');
        expect(id.indexOf('id')).to.be(0);
      });

      it('can use a custom prefix', function() {
        var $el = $('<div>'),
            id = utils.setId($el, 'myprefix');
        expect(id.indexOf('myprefix')).to.be(0);
      });

      it('updates the id of an element with no id', function() {
        var $el = $('<div>'),
            id;
        utils.setId($el);
        id = $el.attr('id');
        expect(id).to.not.be.an('undefined');
        expect(id).to.be.a('string');
        expect(id).to.contain('id');
      });

      it('replaces dots in ids with dashes', function() {
        var $el = $('<div id="something.with.dots"></div>'),
            id = utils.setId($el);
        id = $el.attr('id');
        expect(id).to.equal('something-with-dots');
      });
    });

    describe('parseBodyTag', function() {

      it('parses the body tag\'s content from a response', function() {
        var response = '<body><p>foo</p></body>',
            html = utils.parseBodyTag(response);
        expect(html).to.equal('<p>foo</p>');
      });

      it('returns an empty string for responses with an empty body', function() {
        var response = '<body></body>',
            html = utils.parseBodyTag(response);
        expect(html).to.equal('');
      });

      it('fails for empty responses', function() {
        var response = '',
            fn = function () {utils.parseBodyTag(response);};
        expect(fn).to.throwException(TypeError);
      });

      it('fails for responses without a body tag', function() {
        var response = '<div>qux</div>',
            fn = function () {utils.parseBodyTag(response);};
        expect(fn).to.throwException(TypeError);
      });

    });

    describe('bool', function() {

      it('returns true for "true"', function() {
        expect(utils.bool('true')).to.be.equal(true);
        expect(utils.bool(' true ')).to.be.equal(true);
        expect(utils.bool('TRUE')).to.be.equal(true);
        expect(utils.bool('True')).to.be.equal(true);
      });

      it('returns true for true', function() {
        var val = utils.bool(true);
        expect(val).to.be.equal(true);
      });

      it('returns true for true', function() {
        var val = utils.bool(1);
        expect(val).to.be.equal(true);
      });

      it('returns false for strings != "true"', function() {
        expect(utils.bool('1')).to.be.equal(false);
        expect(utils.bool('')).to.be.equal(false);
        expect(utils.bool('false')).to.be.equal(false);
      });

      it('returns false for undefined/null', function() {
        expect(utils.bool(undefined)).to.be.equal(false);
        expect(utils.bool(null)).to.be.equal(false);
      });
    });


    describe('QueryHelper', function() {

      it('getQueryData correctly', function() {
        var qh = new utils.QueryHelper({vocabularyUrl: 'http://foobar.com/'});
        var qd = qh.getQueryData('foobar');
        expect(qd.query).to.equal('{"criteria":[{"i":"SearchableText","o":"plone.app.querystring.operation.string.contains","v":"foobar*"}],"sort_on":"is_folderish","sort_order":"reverse"}');
      });
      it('getQueryData use attributes correctly', function() {
        var qh = new utils.QueryHelper({
          vocabularyUrl: 'http://foobar.com/',
          attributes: ['one', 'two']
        });
        var qd = qh.getQueryData('foobar');
        expect(qd.attributes).to.equal('["one","two"]');
      });
      it('getQueryData set batch', function() {
        var qh = new utils.QueryHelper({vocabularyUrl: 'http://foobar.com/'});
        var qd = qh.getQueryData('foobar', 1);
        expect(qd.batch).to.equal('{"page":1,"size":' + qh.options.batchSize + '}');
      });

      it('selectAjax gets data correctly', function() {
        var qh = new utils.QueryHelper({vocabularyUrl: 'http://foobar.com/'});
        var sa = qh.selectAjax();
        expect(sa.data('foobar').query).to.equal('{"criteria":[{"i":"SearchableText","o":"plone.app.querystring.operation.string.contains","v":"foobar*"}],"sort_on":"is_folderish","sort_order":"reverse"}');
      });
      it('selectAjax formats results correctly', function() {
        var qh = new utils.QueryHelper({vocabularyUrl: 'http://foobar.com/'});
        var sa = qh.selectAjax();
        var data = sa.results({total: 100, results: [1,2,3]}, 1);
        expect(data.results.length).to.equal(3);
        expect(data.more).to.equal(true);
      });

      it('getUrl correct', function() {
        var qh = new utils.QueryHelper({vocabularyUrl: 'http://foobar.com/'});
        expect(qh.getUrl()).to.equal('http://foobar.com/?query=%7B%22criteria%22%3A%5B%5D%2C%22sort_on%22%3A%22is_folderish%22%2C%22sort_order%22%3A%22reverse%22%7D&attributes=%5B%22UID%22%2C%22Title%22%2C%22Description%22%2C%22getURL%22%2C%22portal_type%22%5D');
      });
      it('getUrl correct and url query params already present', function() {
        var qh = new utils.QueryHelper({vocabularyUrl: 'http://foobar.com/?foo=bar'});
        expect(qh.getUrl()).to.equal('http://foobar.com/?foo=bar&query=%7B%22criteria%22%3A%5B%5D%2C%22sort_on%22%3A%22is_folderish%22%2C%22sort_order%22%3A%22reverse%22%7D&attributes=%5B%22UID%22%2C%22Title%22%2C%22Description%22%2C%22getURL%22%2C%22portal_type%22%5D');
      });


      it('browsing adds path criteria', function() {
        var qh = new utils.QueryHelper({vocabularyUrl: 'http://foobar.com/?foo=bar'});
        qh.pattern.browsing = true;
        expect(qh.getQueryData('foobar').query).to.contain('plone.app.querystring.operation.string.path');
      });


    });

    describe('Loading', function() {

      it('creates element', function() {
        var loading = new utils.Loading();
        expect($('.' + loading.className).length).to.equal(1);
      });
      it('hidden on creation', function() {
        var loading = new utils.Loading();
        expect(loading.$el.is(':visible')).to.equal(false);
      });
      it('shows loader', function() {
        var loading = new utils.Loading();
        loading.show();
        expect(loading.$el.is(':visible')).to.equal(true);
      });
      it('hide loader', function() {
        var loading = new utils.Loading(); 
        loading.show();
        loading.hide();
        expect(loading.$el.is(':visible')).to.equal(false);
      });
      it('test custom zIndex', function() {
        var loading = new utils.Loading({
          zIndex: function() { return 99999; }
        });
        loading.show();
        expect(loading.$el[0].style.zIndex + '').to.equal('99999');
      });
      it('works with backdrop', function() {
        var initCalled = false;
        var showCalled = false;
        var fakeBackdrop = {
          init: function() {
            initCalled = true;
          },
          show: function() {
            showCalled = true;
          }
        };
        var loading = new utils.Loading({
          backdrop: fakeBackdrop
        });
        loading.show();
        expect(initCalled).to.equal(true);
        expect(showCalled).to.equal(true);
        expect(fakeBackdrop.closeOnClick).to.equal(true);
        expect(fakeBackdrop.closeOnEsc).to.equal(true);
      });

    });


  });

});
