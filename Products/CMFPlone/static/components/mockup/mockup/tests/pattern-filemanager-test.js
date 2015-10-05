define([
  'sinon',
  'expect',
  'jquery',
  'pat-registry',
  'mockup-patterns-filemanager'
], function(sinon, expect, $, registry, Tree) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

  describe('File Manager', function() {
    it('loads the file manager', function() {
      this.$el = $('' +
        '<div class="pat-filemanager" ' +
             'data-pat-filemanager="actionUrl:/filemanager-actions;' +
                                 ' ">' +
        '</div>').appendTo('body');

      this.server = sinon.fakeServer.create();
      this.server.autoRespond = true;
      this.clock = sinon.useFakeTimers();

      this.server.respondWith('GET', /filemanager-actions/, function (xhr, id) {
        var data = [{
          label: 'css',
          folder: true,
          children: [{
            label: 'style.css',
            folder: false
          },{
            label: 'tree.css',
            folder: false
          }]
        }];
        xhr.respond(200, { 'Content-Type': 'application/json' }, JSON.stringify(data));
      });

      registry.scan(this.$el);
      this.clock.tick(1000);
      expect(this.$el.find('.tree ul').length).to.be.equal(2);
    });
  });

});