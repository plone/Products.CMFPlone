define([
  'expect',
  'jquery',
  'underscore',
  'sinon',
  'pat-registry',
  'mockup-patterns-relateditems'
], function(expect, $, _, sinon, registry, RelatedItems) {
  'use strict';

  window.mocha.setup('bdd').globals(['jQuery*']);
  $.fx.off = true;

  /* ==========================
   TEST: Related Items
  ========================== */

  describe('Related Items', function() {
    beforeEach(function() {
      this.server = sinon.fakeServer.create();
      this.server.autoRespond = true;

      function getQueryVariable(url, variable) {
        var query = url.split('?')[1];
        if (query === undefined) {
          return null;
        }
        var vars = query.split('&');
        for (var i = 0; i < vars.length; i += 1) {
          var pair = vars[i].split('=');
          if (decodeURIComponent(pair[0]) === variable) {
            return decodeURIComponent(pair[1]);
          }
        }
        return null;
      }
      this.server.respondWith(/relateditems-test.json/, function(xhr, id) {
        var root = [
          {UID: 'jasdlfdlkdkjasdf', Title: 'Some Image', path: '/test.png', portal_type: 'Image', getIcon: "image.png"},
          {UID: 'asdlfkjasdlfkjasdf', Title: 'News', path: '/news', portal_type: 'Folder', getIcon: ""},
          {UID: '124asdfasasdaf34', Title: 'About', path: '/about', portal_type: 'Folder', getIcon: ""},
          {UID: 'asdf1234', Title: 'Projects', path: '/projects', portal_type: 'Folder', getIcon: ""},
          {UID: 'asdf1234gsad', Title: 'Contact', path: '/contact', portal_type: 'Document', getIcon: "document.png"},
          {UID: 'asdv34sdfs', Title: 'Privacy Policy', path: '/policy', portal_type: 'Document', getIcon: ""},
          {UID: 'asdfasdf234sdf', Title: 'Our Process', path: '/our-process', portal_type: 'Folder', getIcon: "folder.png"},
          {UID: 'asdhsfghyt45', Title: 'Donate', path: '/donate-now', portal_type: 'Document', getIcon: ""},
        ];
        var about = [
          {UID: 'gfn5634f', Title: 'About Us', path: '/about/about-us', portal_type: 'Document', getIcon: ""},
          {UID: '45dsfgsdcd', Title: 'Philosophy', path: '/about/philosophy', portal_type: 'Document', getIcon: ""},
          {UID: 'dfgsdfgj675', Title: 'Staff', path: '/about/staff', portal_type: 'Folder', getIcon: ""},
          {UID: 'sdfbsfdh345', Title: 'Board of Directors', path: '/about/board-of-directors', portal_type: 'Document', getIcon: ""}
        ];

        var staff = [
          {UID: 'asdfasdf9sdf', Title: 'Mike', path: '/about/staff/mike', portal_type: 'Document', getIcon: ""},
          {UID: 'cvbcvb82345', Title: 'Joe', path: '/about/staff/joe', portal_type: 'Document', getIcon: ""}
        ];
        var searchables = about.concat(root).concat(staff);

        var addUrls = function(list) {
          /* add getURL value */
          for (var i = 0; i < list.length; i = i + 1) {
            var data = list[i];
            data.getURL = window.location.origin + data.path;
          }
        };
        addUrls(searchables);
        addUrls(root);
        root[0].getURL = window.location.origin + '/exampledata/test.png';

        var results = [];

        // grab the page number and number of items per page -- note, page is 1-based from Select2
        var batch = getQueryVariable(xhr.url, 'batch');
        var page = 1;
        var pageSize = 10;
        if (batch) {
          batch = $.parseJSON(batch);
          page = batch.page;
          pageSize = batch.size;
        }
        page = page - 1;

        var query = getQueryVariable(xhr.url, 'query');
        var path = null;
        var term = '';
        if (query) {
          query = $.parseJSON(query);
          for (var i = 0; i < query.criteria.length; i = i + 1) {
            var criteria = query.criteria[i];
            if (criteria.i === 'path') {
              path = criteria.v.split('::')[0];
            } else {
              term = criteria.v;
            }
          }
        }

        // this seach is for basically searching the entire hierarchy -- this IS NOT the browse "search"
        function search(items, term) {
          results = [];
          if (term === undefined) {
            return searchables;
          }
          _.each(items, function(item) {
            var q;
            var keys = (item.UID + ' ' + item.Title + ' ' + item.path + ' ' + item.portal_type).toLowerCase();
            if (typeof(term) === 'object') {
              for (var i = 0; i < term.length; i = i + 1) {
                q = term[i].toLowerCase();
                if (keys.indexOf(q) > -1) {
                  results.push(item);
                  break;
                }
              }
            } else {
              q = term.toLowerCase();
              if (keys.indexOf(q) > -1) {
                results.push(item);
              }
            }
          });
        }

        function browse(items, q, p) {
          results = [];
          var path = p.substring(0, p.length - 1);
          var splitPath = path.split('/');
          var fromPath = [];
          _.each(items, function(item) {
            var itemSplit = item.path.split('/');
            if (item.path.indexOf(path) === 0 && itemSplit.length - 1 === splitPath.length) {
              fromPath.push(item);
            }
          });
          if (q === undefined) {
            return fromPath;
          }
          search(fromPath, q);
        }
        if (path) {
          browse(searchables, term, path);
        } else {
          search(searchables, term);
        }

        xhr.respond(200, { 'Content-Type': 'application/json' },
          JSON.stringify({
            total: results.length,
            results: results.slice(page * pageSize, (page * pageSize) + (pageSize - 1))
          })
        );
      });
    });

    it('test initialize', function() {
      var $el = $('' +
        '<div>' +
        ' <input class="pat-relateditems"' +
        '        data-pat-relateditems="width: 300px;' +
        '                          vocabularyUrl: /relateditems-test.json" />' +
        '</div>').appendTo('body');
      var pattern = $('.pat-relateditems', $el).patternRelateditems().data('patternRelateditems');

      expect($('.select2-container-multi', $el)).to.have.length(1);
      expect($('.pattern-relateditems-container', $el)).to.have.length(1);
      expect($('.pattern-relateditems-path', $el)).to.have.length(1);

      $el.remove();
      $('.select2-sizer, .select2-drop').remove();
    });

    it('select an item by clicking add button', function () {
      var $el = $('' +
        '<div>' +
        ' <input class="pat-relateditems"' +
        '        data-pat-relateditems="width: 300px;' +
        '                          vocabularyUrl: /relateditems-test.json" />' +
        '</div>').appendTo('body');
      var pattern = $('.pat-relateditems', $el).patternRelateditems().data('patternRelateditems');

      var clock = sinon.useFakeTimers();
      pattern.$el.select2('open');
      clock.tick(1000);
      expect(pattern.$el.select2('data')).to.have.length(0);
      expect($('.pattern-relateditems-result-select')).to.have.length(13);
      $('.pattern-relateditems-result-select').first().on('click', function() {
        expect(pattern.$el.select2('data')).to.have.length(1);
        expect(pattern.$el.select2('val')[0]).to.equal('gfn5634f');
      }).click();
      clock.tick(1000);

      $el.remove();
      $('.select2-sizer, .select2-drop').remove();
    });

    it('deselect an item from selected items using click', function () {
      var $el = $('' +
        '<div>' +
        ' <input class="pat-relateditems"' +
        '        data-pat-relateditems="width: 300px;' +
        '                          vocabularyUrl: /relateditems-test.json" />' +
        '</div>').appendTo('body');
      var pattern = $('.pat-relateditems', $el).patternRelateditems().data('patternRelateditems');

      var clock = sinon.useFakeTimers();

      pattern.$el.select2('open');
      clock.tick(1000);

      $('.pattern-relateditems-result-select').first().on('click', function() {
        expect(pattern.$el.select2('data')).to.have.length(1);
      }).click();
      clock.tick(1000);
      // deselect our first choice
      var $choice = $('.select2-search-choice').first();
      $choice.find('.select2-search-choice-close').click();
      expect(pattern.$el.select2('data')).to.have.length(0);
      expect(pattern.$el.select2('val')).to.have.length(0);

      // // Need to simulate a backspace to remove the selected item: below doesn't work
      // var backspaceEvent = $.Event('keydown');
      // backspaceEvent.ctrlKey = false;
      // backspaceEvent.which = 8;
      // $('.select2-search-field input').trigger( backspaceEvent );
      // expect(pattern.$el.select2('data')).to.have.length(0);

      $el.remove();
      $('.select2-sizer, .select2-drop').remove();
    });

    it('deselect an item from results using click', function () {
      var $el = $('' +
        '<div>' +
        ' <input class="pat-relateditems"' +
        '        data-pat-relateditems="width: 300px;' +
        '                          vocabularyUrl: /relateditems-test.json" />' +
        '</div>').appendTo('body');
      var pattern = $('.pat-relateditems', $el).patternRelateditems().data('patternRelateditems');

      var clock = sinon.useFakeTimers();

      pattern.$el.select2('open');
      clock.tick(1000);

      var $result = $('.pattern-relateditems-result').first();

      expect($result.is('.pattern-relateditems-active')).to.equal(false);

      $('.pattern-relateditems-result-select', $result).click();
      expect(pattern.$el.select2('data')).to.have.length(1);

      expect($result.is('.pattern-relateditems-active')).to.equal(true);
      $('.pattern-relateditems-result-select', $result).click();

      expect($result.is('.pattern-relateditems-active')).to.equal(false);
      expect(pattern.$el.select2('data')).to.have.length(0);
      expect(pattern.$el.select2('val')).to.have.length(0);

      $el.remove();
      $('.select2-sizer, .select2-drop').remove();
    });

    it('allow only a single type to be selectable', function () {
      var $el = $('' +
        '<div>' +
        ' <input class="pat-relateditems" />' +
        '</div>').appendTo('body');
      var opts = {
        vocabularyUrl: '/relateditems-test.json',
        selectableTypes: ['Image']
      };
      var pattern = $('.pat-relateditems', $el).attr('data-pat-relateditems', JSON.stringify(opts)).patternRelateditems().data('patternRelateditems');

      var clock = sinon.useFakeTimers();

      pattern.$el.select2('open');
      clock.tick(1000);
      expect(pattern.$el.select2('data')).to.have.length(0);

      $('.pattern-relateditems-result-select').first().click();
      expect(pattern.$el.select2('data')).to.have.length(0);

      $('.pattern-relateditems-type-Image .pattern-relateditems-result-select').first().click();
      expect(pattern.$el.select2('data')).to.have.length(1);

      $el.remove();
      $('.select2-sizer, .select2-drop').remove();
    });

    it('clicking folder button filters to that folder', function() {
      var $el = $('' +
        '<div>' +
        ' <input class="pat-relateditems"' +
        '        data-pat-relateditems="width: 300px;' +
        '                          vocabularyUrl: /relateditems-test.json" />' +
        '</div>').appendTo('body');
      var pattern = $('.pat-relateditems', $el).patternRelateditems().data('patternRelateditems');

      var clock = sinon.useFakeTimers();

      pattern.$el.select2('open');
      clock.tick(1000);
      var $items = $('.select2-results > li');
      expect(pattern.browsing).to.be.equal(false);
      expect($('.pattern-relateditems-result-browse', $items)).to.have.length(5);
      $('.pattern-relateditems-result-browse', $items).first().on('click', function() {
        expect(pattern.browsing).to.be.equal(true);
        expect(pattern.currentPath).to.equal($(this).attr('data-path'));
      }).click();

      $el.remove();
      $('.select2-sizer, .select2-drop, .select2-drop-mask').remove();
    });

    it('after selecting a folder, it remains in the results list', function() {
      var $el = $('' +
        '<div>' +
        ' <input class="pat-relateditems"' +
        '        data-pat-relateditems="width: 300px;' +
        '                          vocabularyUrl: /relateditems-test.json" />' +
        '</div>').appendTo('body');
      var pattern = $('.pat-relateditems', $el).patternRelateditems().data('patternRelateditems');

      var clock = sinon.useFakeTimers();
      pattern.$el.select2('open');
      clock.tick(1000);
      expect(pattern.$el.select2('data')).to.have.length(0);
      expect($('.pattern-relateditems-result-select')).to.have.length(13);
      $('.pattern-relateditems-result-path')
        .filter(function() { return $(this).text() === '/about'; })
        .click();
      clock.tick(1000);
      expect(pattern.$el.select2('val')[0]).to.equal('124asdfasasdaf34');
      var result = $('.pattern-relateditems-result-path')
        .filter(function() { return $(this).text() === '/about'; });
      expect(result.length).to.equal(1);

      $el.remove();
      $('.select2-sizer, .select2-drop').remove();
    });

    it('clicking on breadcrumbs goes back up', function() {
      var $el = $('' +
        '<div>' +
        ' <input class="pat-relateditems"' +
        '        data-pat-relateditems="width: 300px;' +
        '                          vocabularyUrl: /relateditems-test.json" />' +
        '</div>').appendTo('body');
      var pattern = $('.pat-relateditems', $el).patternRelateditems().data('patternRelateditems');

      var clock = sinon.useFakeTimers();
      pattern.$el.select2('open');

      clock.tick(1000);
      var $items = $('.select2-results > li');
      expect(pattern.browsing).to.be.equal(false);
      expect($('.pattern-relateditems-result-browse', $items)).to.have.length(5);
      $('.pattern-relateditems-result-browse', $items).first().click();
      clock.tick(1000);
      var $crumbs = $('.pattern-relateditems-path a.crumb');
      // /about/staff
      expect($crumbs).to.have.length(3);
      // /about
      $crumbs.eq(1).on('click', function() {
      }).click();
      clock.tick(1000);
      expect(pattern.currentPath).to.equal('/about');

      $el.remove();
      $('.select2-sizer, .select2-drop, .select2-drop-mask').remove();
    });

    it('maximum number of selected items', function() {
      var $el = $('' +
        '<div>' +
        ' <input class="pat-relateditems"' +
        '        data-pat-relateditems="width: 300px;' +
        '                          maximumSelectionSize: 1;' +
        '                          vocabularyUrl: /relateditems-test.json" />' +
        '</div>').appendTo('body');
      var pattern = $('.pat-relateditems', $el).patternRelateditems().data('patternRelateditems');

      var clock = sinon.useFakeTimers();
      pattern.$el.select2('open');
      clock.tick(1000);

      $('.pattern-relateditems-result-select').first().click();
      expect(pattern.$el.select2('data')).to.have.length(1);
      $('.pattern-relateditems-result-select').last().click();
      expect(pattern.$el.select2('data')).to.have.length(1);

      $el.remove();
      $('.select2-sizer, .select2-drop, .select2-drop-mask').remove();
    });

    it('init selection', function() {
      var $el = $('' +
        '<div>' +
        ' <input class="pat-relateditems"' +
        '        value="asdf1234,sdfbsfdh345,asdlfkjasdlfkjasdf,kokpoius98"' +
        '        data-pat-relateditems="width: 300px;' +
        '                          maximumSelectionSize: 1;' +
        '                          vocabularyUrl: /relateditems-test.json" />' +
        '</div>').appendTo('body');
      var pattern = $('.pat-relateditems', $el).patternRelateditems().data('patternRelateditems');

      var clock = sinon.useFakeTimers();
      pattern.$el.select2('open');
      clock.tick(1000);

      $el.remove();
      $('.select2-sizer, .select2-drop, .select2-drop-mask').remove();
    });

    it('test tree initialized', function() {
      var $el = $('' +
        '<div>' +
        ' <input class="pat-relateditems"' +
        '        value="asdf1234,sdfbsfdh345,asdlfkjasdlfkjasdf,kokpoius98"' +
        '        data-pat-relateditems="width: 300px;' +
        '                          maximumSelectionSize: 1;' +
        '                          vocabularyUrl: /relateditems-test.json" />' +
        '</div>').appendTo('body');

      var clock = sinon.useFakeTimers();
      var pattern = $('.pat-relateditems', $el).patternRelateditems().data('patternRelateditems');

      clock.tick(1000);

      $el.find('.pattern-relateditems-tree-select').trigger('click');

      clock.tick(1000);

      expect($el.find('.pat-tree ul li').length).to.equal(4);

      $el.remove();
      $('.select2-sizer, .select2-drop, .select2-drop-mask').remove();
    });

    it('test tree select', function() {
      var $el = $('' +
        '<div>' +
        ' <input class="pat-relateditems"' +
        '        value="asdf1234,sdfbsfdh345,asdlfkjasdlfkjasdf,kokpoius98"' +
        '        data-pat-relateditems="width: 300px;' +
        '                          maximumSelectionSize: 1;' +
        '                          vocabularyUrl: /relateditems-test.json" />' +
        '</div>').appendTo('body');

      var clock = sinon.useFakeTimers();
      $('.pat-relateditems', $el).patternRelateditems().data('patternRelateditems');

      clock.tick(1000);

      expect($el.find('.crumb').length).to.equal(1);

      $el.find('.pattern-relateditems-tree-select').trigger('click');
      clock.tick(1000);

      $el.find('.pat-tree ul li .pattern-relateditems-buttons a').eq(2).trigger('click');
      clock.tick(1000);

      expect($el.find('.crumb').length).to.equal(2);

      $el.remove();
      $('.select2-sizer, .select2-drop, .select2-drop-mask').remove();
    });

    it('test tree sub select', function() {
      var $el = $('' +
        '<div>' +
        ' <input class="pat-relateditems"' +
        '        value="asdf1234,sdfbsfdh345,asdlfkjasdlfkjasdf,kokpoius98"' +
        '        data-pat-relateditems="width: 300px;' +
        '                          maximumSelectionSize: 1;' +
        '                          vocabularyUrl: /relateditems-test.json" />' +
        '</div>').appendTo('body');

      var clock = sinon.useFakeTimers();
      $('.pat-relateditems', $el).patternRelateditems().data('patternRelateditems');

      clock.tick(1000);

      expect($el.find('.crumb').length).to.equal(1);

      $el.find('.pattern-relateditems-tree-select').trigger('click');
      clock.tick(1000);

      $el.find('.pat-tree ul li div').eq(1).trigger('click');
      clock.tick(1000);

      $el.find('.pat-tree ul li .pattern-relateditems-buttons a').eq(2).trigger('click');
      clock.tick(1000);

      expect($el.find('.crumb').length).to.equal(3);

      $el.remove();
      $('.select2-sizer, .select2-drop, .select2-drop-mask').remove();
    });

    it('test tree cancel', function() {
      var $el = $('' +
        '<div>' +
        ' <input class="pat-relateditems"' +
        '        value="asdf1234,sdfbsfdh345,asdlfkjasdlfkjasdf,kokpoius98"' +
        '        data-pat-relateditems="width: 300px;' +
        '                          maximumSelectionSize: 1;' +
        '                          vocabularyUrl: /relateditems-test.json" />' +
        '</div>').appendTo('body');

      var clock = sinon.useFakeTimers();
      $('.pat-relateditems', $el).patternRelateditems().data('patternRelateditems');

      clock.tick(1000);

      expect($el.find('.crumb').length).to.equal(1);

      $el.find('.pattern-relateditems-tree-select').trigger('click');
      clock.tick(1000);

      $el.find('.pattern-relateditems-tree-cancel').trigger('click');
      clock.tick(1000);

      expect($el.find('.crumb').length).to.equal(1);
      expect($el.find('.tree-container').is(':visible')).to.equal(false);

      $el.remove();
      $('.select2-sizer, .select2-drop, .select2-drop-mask').remove();
    });



  });

});
