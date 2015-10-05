define([
  'expect',
  'jquery',
  'sinon',
  'pat-registry',
  'mockup-patterns-livesearch'
], function(expect, $, sinon, registry, Livesearch) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

   /* ==========================
   TEST: Livesearch 
  ========================== */

  describe('Livesearch', function() {
    beforeEach(function() {
      this.server = sinon.fakeServer.create();
      this.server.autoRespond = true;

      this.server.respondWith('GET', /livesearch\.json/, function (xhr, id) {
        var items = [];
        for(var i=0; i<7; i=i+1){
          items.push({
            url: 'http://localhost:8081/news/aggregator',
            description: 'Site News',
            title: 'News',
            state: 'published'
          });
        }
        xhr.respond(200, { 'Content-Type': 'application/json' }, JSON.stringify({
          total: items.length * 2,
          items: items
        }));
      });
      this.clock = sinon.useFakeTimers();

      this.$el = $('' +
        '<form class="pat-livesearch">' +
        ' <input type="text" value="foobar" />' +
        '</form>').appendTo($('body'));

      this.ls = new Livesearch(this.$el, {
        ajaxUrl: 'livesearch.json'
      });
    });

    afterEach(function() {
      $('body').empty();
      this.server.restore();
      this.clock.restore();
      this.$el.remove();
    });

    it('results on focus', function() {
      this.ls.$input.trigger('focusin');
      this.clock.tick(1000);
      expect(this.$el.find('.livesearch-results li').size()).to.equal(9);
    });

    it('responds to keyup', function() {
      this.ls.$input.trigger('keyup');
      this.clock.tick(1000);
      expect(this.$el.find('.livesearch-results li').size()).to.equal(9);
    });

    it('does not show with minimum length not met', function() {
      this.ls.$input.attr('value', 'fo');
      this.ls.$input.trigger('keyup');
      this.clock.tick(1000);
      expect(this.$el.find('.livesearch-results li').size()).to.equal(1);
    });

    it('focus out hides', function() {
      this.ls.$input.trigger('keyup');
      this.clock.tick(1000);
      expect(this.$el.find('.livesearch-results li').size()).to.equal(9);

      this.ls.$input.trigger('focusout');
      this.clock.tick(1000);
      expect(this.$el.find('.livesearch-results').is(':visible')).to.equal(false);

    });

    it('focus back in shows already searched', function() {
      this.ls.$input.trigger('keyup');
      this.clock.tick(1000);
      expect(this.$el.find('.livesearch-results li').size()).to.equal(9);

      this.ls.$input.trigger('focusout');
      this.clock.tick(1000);
      expect(this.$el.find('.livesearch-results').is(':visible')).to.equal(false);

      this.ls.$input.trigger('focusin');
      this.clock.tick(1000);
      expect(this.$el.find('.livesearch-results').is(':visible')).to.equal(true);
    });

    it('should show next and prev', function() {
      this.ls.$input.trigger('keyup');
      this.clock.tick(1000);
      expect(this.$el.find('.livesearch-results li').size()).to.equal(9);
      expect(this.$el.find('.livesearch-results li a.next').size()).to.equal(1);

      this.ls.doSearch(2);
      this.clock.tick(1000);

      expect(this.$el.find('.livesearch-results li').size()).to.equal(9);
      expect(this.$el.find('.livesearch-results li a.prev').size()).to.equal(1);
    });

  });

});
