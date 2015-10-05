define([
  'expect',
  'jquery',
  'sinon',
  'pat-registry',
  'mockup-patterns-modal'
], function(expect, $, sinon, registry, Modal) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

  /* ==========================
   TEST: Modal
  ========================== */

  describe('Modal', function() {
    beforeEach(function() {
      this.server = sinon.fakeServer.create();
      this.server.autoRespond = true;
      this.server.respondWith(/patterns-modal-load-via-ajax/, function (xhr, id) {
        xhr.respond(200, { 'Content-Type': 'text/html' }, '' +
          '<html><body>' +
          '<div id="content">Exampel</div>' +
          '</body></html>'
        );
      });

      this.server.respondWith('GET', /modal-form\.html/, function (xhr, id) {
        xhr.respond(200, { 'Content-Type': 'text/html' },
          '<html>' +
          '<head></head>' +
          '<body>' +
          '<div id="content">' +
          '<h1>Modal with Form</h1>' +
          '<p>This modal contains a form.</p>' +
          '<form method="POST" action="/modal-submit.html">' +
          '  <label for="name">Name:</label><input type="text" name="name" />' +
          '  <div class="formControls"> ' +
          '    <input type="submit" class="btn btn-primary" value="Submit" name="save" />' +
          '  </div>' +
          '</form>' +
          '</body>' +
          '</html>'
        );
      });

      this.server.respondWith('POST', /modal-submit\.html/, function(xhr, id) {
        xhr.respond(200, {'content-Type': 'text/html'},
          '<html> ' +
          '  <head></head>' +
          '  <body> ' +
          '    <div id="content">' +
          '      <h1>Form submitted</h1>' +
          '      <p>Thanks!</p>' +
          '  </body> ' +
          '</html>'
        );
      });
    });

    afterEach(function() {
      $('body').empty();
      this.server.restore();
    });

    it('default behaviour', function() {
      var $el = $('' +
        '<div id="body">' +
        ' <a class="pat-plone-modal" href="#target"' +
        '    data-pat-plone-modal="backdrop: #body">Open</a>' +
        ' <div id="target" style="display:none;">Target</div>' +
        '</div>').appendTo('body');

      registry.scan($el);

      expect($('.plone-modal-backdrop', $el).is(':hidden')).to.be.equal(true);
      expect($el.hasClass('plone-backdrop-active')).to.be.equal(false);
      expect($('.plone-modal-wrapper', $el).is(':hidden')).to.be.equal(true);
      expect($('.plone-modal', $el).size()).to.equal(0);

      $('a.pat-plone-modal', $el).click();

      expect($('.plone-modal-backdrop', $el).is(':visible')).to.be.equal(true);
      expect($el.hasClass('plone-backdrop-active')).to.be.equal(true);
      expect($('.plone-modal-wrapper', $el).is(':visible')).to.be.equal(true);
      expect($('.plone-modal', $el).size()).to.equal(1);
      expect($('.plone-modal', $el).hasClass('in')).to.be.equal(true);
      expect($('.plone-modal .plone-modal-header', $el).size()).to.equal(1);
      expect($('.plone-modal .plone-modal-body', $el).size()).to.equal(1);
      expect($('.plone-modal .plone-modal-footer', $el).size()).to.equal(1);

      var keydown = $.Event('keydown');
      keydown.keyCode = 27;
      $(document).trigger(keydown);
      expect($el.hasClass('plone-backdrop-active')).to.be.equal(false);
      expect($('.plone-modal', $el).size()).to.equal(0);

      $el.remove();
    });

    it('customize modal on show event', function() {
      var $el = $('' +
        '<div id="body">' +
        ' <a class="pat-plone-modal" href="#target"' +
        '    data-pat-plone-modal="backdrop: #body">Open</a>' +
        ' <div id="target">Target</div>' +
        '</div>').appendTo('body');

      $('a', $el)
        .patPloneModal()
        .on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          $('.plone-modal-header', modal.$modal).prepend($('<h3>New Title</h3>'));
        })
        .click();
      expect($('.plone-modal .plone-modal-header h3', $el).text()).to.equal('New Title');

      $el.remove();
    });

    it('load modal content via ajax', function(done) {
      $('<a class="pat-plone-modal" />')
        .patPloneModal()
        .on('show.plone-modal.patterns', function(e) {
          expect(true).to.be.equal(true);
          done();
        })
        .click();
    });

    it('redirects to base urls', function(done) {
      $('<a class="pat-plone-modal" />')
        .patPloneModal()
        .on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          expect(modal.defaults.actionOptions.redirectToUrl(
            'ignore',
            '<html><head><base href="testurl1"></base></head></html>'
          )).to.equal('testurl1');
          expect(modal.defaults.actionOptions.redirectToUrl(
            'ignore',
            '<html><head><base href="testurl2" /></head></html>'
          )).to.equal('testurl2');
          expect(modal.defaults.actionOptions.redirectToUrl(
            'ignore',
            '<html><body data-base-url="testurl3" rubbish="discarded"></body></html>'
          )).to.equal('testurl3');
          expect(modal.defaults.actionOptions.redirectToUrl(
            'ignore',
            '<html><body data-view-url="testurl4" rubbish="discarded"></body></html>'
          )).to.equal('testurl4');
          done();
        })
        .click();
    });

    it('handles forms and form submits', function(done) {
      var server = this.server;
      $('<a href="modal-form.html" class="pat-plone-modal" >Foo</a>')
        .appendTo('body')
        .patPloneModal()
        .on('show.plone-modal.patterns', function(e) {
          var $input = $('.pattern-modal-buttons').find('input');
          expect($input.size()).to.equal(1);
          $input.click();
          server.respond(); // XXX could not get autorespond to work
        })
        .on('formActionSuccess.plone-modal.patterns', function() {
          expect($('.plone-modal').hasClass('in')).to.be.equal(true);
          var title = $('.plone-modal-header').find('h2').text();
          expect(title).to.equal('Form submitted');
          done();
        })
      .click();
      server.respond(); // XXX could not get autorespond to work
    });


    it('handles form submits with enter key', function(done) {
      var server = this.server;
      $('<a href="modal-form.html" class="pat-plone-modal" >Foo</a>')
        .appendTo('body')
        .patPloneModal()
        .on('show.plone-modal.patterns', function(e) {
          var event = $.Event ('keydown');
          event.which = event.keyCode = 13;
          $('.plone-modal form').trigger (event);
          server.respond();
        })
        .on('formActionSuccess.plone-modal.patterns', function() {
          var title = $('.plone-modal-header').find('h2').text();
          expect(title).to.equal('Form submitted');
          done();
        })
        .click();
      server.respond();
    });

    describe('modal positioning (findPosition) ', function() {
      //
      // -- CHANGE POSITION ONLY ----------------------------------------------
      //
      it('position: center middle, margin: 0, modal: 340x280, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('center', 'middle', 0, 340, 280, 400, 300);
          expect(pos).not.to.have.property('bottom');
          expect(pos).to.have.property('top');
          // half wrapper height - half modal height - margin
          // 300/2 - 280/2 - 0 = 150 - 140 = 10
          expect(pos.top).to.equal('10px');

          expect(pos).not.to.have.property('right');
          expect(pos).to.have.property('left');
          // half wrapper width - half modal width - margin
          // 400/2 - 340/2 - 0 = 200 - 170 = 30
          expect(pos.left).to.equal('30px');
          done();
        }).click();
      });
      it('position: left middle, margin: 0, modal: 340x280, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('left', 'middle', 0, 340, 280, 400, 300);
          expect(pos).not.to.have.property('bottom');
          expect(pos).to.have.property('top');
          // half wrapper height - half modal height - margin
          // 300/2 - 280/2 - 0 = 150 - 140 = 10
          expect(pos.top).to.equal('10px');

          expect(pos).not.to.have.property('right');
          expect(pos).to.have.property('left');
          expect(pos.left).to.equal('0px');
          done();
        }).click();
      });
      it('position: right middle, margin: 0, modal: 340x280, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('right', 'middle', 0, 340, 280, 400, 300);
          expect(pos).not.to.have.property('bottom');
          expect(pos).to.have.property('top');
          // half wrapper height - half modal height - margin
          // 300/2 - 280/2 - 0 = 150 - 140 = 10
          expect(pos.top).to.equal('10px');

          expect(pos).to.have.property('right');
          expect(pos).to.have.property('left');
          expect(pos.right).to.equal('0px');
          expect(pos.left).to.equal('auto');
          done();
        }).click();
      });
      it('position: center top, margin: 0, modal: 340x280, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('center', 'top', 0, 340, 280, 400, 300);
          expect(pos).not.to.have.property('bottom');
          expect(pos).to.have.property('top');
          expect(pos.top).to.equal('0px');

          expect(pos).not.to.have.property('right');
          expect(pos).to.have.property('left');
          // half wrapper width - half modal width - margin
          // 400/2 - 340/2 - 0 = 200 - 170 = 30
          expect(pos.left).to.equal('30px');
          done();
        }).click();
      });
      it('position: center bottom, margin: 0, modal: 340x280, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('center', 'bottom', 0, 340, 280, 400, 300);
          expect(pos).to.have.property('bottom');
          expect(pos).to.have.property('top');
          expect(pos.bottom).to.equal('0px');
          expect(pos.top).to.equal('auto');

          expect(pos).not.to.have.property('right');
          expect(pos).to.have.property('left');
          // half wrapper width - half modal width - margin
          // 400/2 - 340/2 - 0 = 200 - 170 = 30
          expect(pos.left).to.equal('30px');
          done();
        }).click();
      });
      it('position: left top, margin: 0, modal: 340x280, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('left', 'top', 0, 340, 280, 400, 300);
          expect(pos).not.to.have.property('bottom');
          expect(pos).to.have.property('top');
          expect(pos.top).to.equal('0px');

          expect(pos).not.to.have.property('right');
          expect(pos).to.have.property('left');
          expect(pos.left).to.equal('0px');
          done();
        }).click();
      });
      it('position: left bottom, margin: 0, modal: 340x280, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('left', 'bottom', 0, 340, 280, 400, 300);
          expect(pos).to.have.property('bottom');
          expect(pos).to.have.property('top');
          expect(pos.bottom).to.equal('0px');
          expect(pos.top).to.equal('auto');

          expect(pos).not.to.have.property('right');
          expect(pos).to.have.property('left');
          expect(pos.left).to.equal('0px');
          done();
        }).click();
      });
      it('position: right top, margin: 0, modal: 340x280, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('right', 'top', 0, 340, 280, 400, 300);
          expect(pos).not.to.have.property('bottom');
          expect(pos).to.have.property('top');
          expect(pos.top).to.equal('0px');

          expect(pos).to.have.property('right');
          expect(pos).to.have.property('left');
          expect(pos.right).to.equal('0px');
          expect(pos.left).to.equal('auto');
          done();
        }).click();
      });
      it('position: right bottom, margin: 0, modal: 340x280, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('right', 'bottom', 0, 340, 280, 400, 300);
          expect(pos).to.have.property('bottom');
          expect(pos).to.have.property('top');
          expect(pos.bottom).to.equal('0px');
          expect(pos.top).to.equal('auto');

          expect(pos).to.have.property('right');
          expect(pos).to.have.property('left');
          expect(pos.right).to.equal('0px');
          expect(pos.left).to.equal('auto');
          done();
        }).click();
      });

      //
      // -- NON-ZERO MARGIN ---------------------------------------------------
      //
      it('position: center middle, margin: 5, modal: 340x280, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('center', 'middle', 5, 340, 280, 400, 300);
          expect(pos).not.to.have.property('bottom');
          expect(pos).to.have.property('top');
          // half wrapper height - half modal height - margin
          // 300/2 - 280/2 - 5 = 150 - 140 - 5 = 5
          expect(pos.top).to.equal('5px');

          expect(pos).not.to.have.property('right');
          expect(pos).to.have.property('left');
          // half wrapper width - half modal width - margin
          // 400/2 - 340/2 - 5 = 200 - 170 - 5 = 25
          expect(pos.left).to.equal('25px');
          done();
        }).click();
      });
      it('position: left middle, margin: 5, modal: 340x280, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('left', 'middle', 5, 340, 280, 400, 300);
          expect(pos).not.to.have.property('bottom');
          expect(pos).to.have.property('top');
          // half wrapper height - half modal height - margin
          // 300/2 - 280/2 - 5 = 150 - 140 = 5
          expect(pos.top).to.equal('5px');

          expect(pos).not.to.have.property('right');
          expect(pos).to.have.property('left');
          expect(pos.left).to.equal('5px');
          done();
        }).click();
      });
      it('position: right middle, margin: 5, modal: 340x280, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('right', 'middle', 5, 340, 280, 400, 300);
          expect(pos).not.to.have.property('bottom');
          expect(pos).to.have.property('top');
          // half wrapper height - half modal height - margin
          // 300/2 - 280/2 - 5 = 150 - 140 - 5 = 5
          expect(pos.top).to.equal('5px');

          expect(pos).to.have.property('right');
          expect(pos).to.have.property('left');
          expect(pos.right).to.equal('5px');
          expect(pos.left).to.equal('auto');
          done();
        }).click();
      });
      it('position: center top, margin: 5, modal: 340x280, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('center', 'top', 5, 340, 280, 400, 300);
          expect(pos).not.to.have.property('bottom');
          expect(pos).to.have.property('top');
          expect(pos.top).to.equal('5px');

          expect(pos).not.to.have.property('right');
          expect(pos).to.have.property('left');
          // half wrapper width - half modal width - margin
          // 400/2 - 340/2 - 5 = 200 - 170 - 5 = 25
          expect(pos.left).to.equal('25px');
          done();
        }).click();
      });
      it('position: center bottom, margin: 5, modal: 340x280, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('center', 'bottom', 5, 340, 280, 400, 300);
          expect(pos).to.have.property('bottom');
          expect(pos).to.have.property('top');
          expect(pos.bottom).to.equal('5px');
          expect(pos.top).to.equal('auto');

          expect(pos).not.to.have.property('right');
          expect(pos).to.have.property('left');
          // half wrapper width - half modal width - margin
          // 400/2 - 340/2 - 5 = 200 - 170 - 5 = 25
          expect(pos.left).to.equal('25px');
          done();
        }).click();
      });
      it('position: left top, margin: 5, modal: 340x280, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('left', 'top', 5, 340, 280, 400, 300);
          expect(pos).not.to.have.property('bottom');
          expect(pos).to.have.property('top');
          expect(pos.top).to.equal('5px');

          expect(pos).not.to.have.property('right');
          expect(pos).to.have.property('left');
          expect(pos.left).to.equal('5px');
          done();
        }).click();
      });
      it('position: left bottom, margin: 5, modal: 340x280, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('left', 'bottom', 5, 340, 280, 400, 300);
          expect(pos).to.have.property('bottom');
          expect(pos).to.have.property('top');
          expect(pos.bottom).to.equal('5px');
          expect(pos.top).to.equal('auto');

          expect(pos).not.to.have.property('right');
          expect(pos).to.have.property('left');
          expect(pos.left).to.equal('5px');
          done();
        }).click();
      });
      it('position: right top, margin: 5, modal: 340x280, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('right', 'top', 5, 340, 280, 400, 300);
          expect(pos).not.to.have.property('bottom');
          expect(pos).to.have.property('top');
          expect(pos.top).to.equal('5px');

          expect(pos).to.have.property('right');
          expect(pos).to.have.property('left');
          expect(pos.right).to.equal('5px');
          expect(pos.left).to.equal('auto');
          done();
        }).click();
      });
      it('position: right bottom, margin: 5, modal: 340x280, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('right', 'bottom', 5, 340, 280, 400, 300);
          expect(pos).to.have.property('bottom');
          expect(pos).to.have.property('top');
          expect(pos.bottom).to.equal('5px');
          expect(pos.top).to.equal('auto');

          expect(pos).to.have.property('right');
          expect(pos).to.have.property('left');
          expect(pos.right).to.equal('5px');
          expect(pos.left).to.equal('auto');
          done();
        }).click();
      });

      //
      // -- WRAPPER SMALLER THAN MODAL ----------------------------------------
      //
      it('position: center middle, margin: 0, modal: 450x350, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('center', 'middle', 0, 450, 350, 400, 300);
          expect(pos).not.to.have.property('bottom');
          expect(pos).to.have.property('top');
          expect(pos.top).to.equal('0px');

          expect(pos).not.to.have.property('right');
          expect(pos).to.have.property('left');
          expect(pos.left).to.equal('0px');
          done();
        }).click();
      });
      it('position: left middle, margin: 0, modal: 450x350, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('left', 'middle', 0, 450, 350, 400, 300);
          expect(pos).not.to.have.property('bottom');
          expect(pos).to.have.property('top');
          expect(pos.top).to.equal('0px');

          expect(pos).not.to.have.property('right');
          expect(pos).to.have.property('left');
          expect(pos.left).to.equal('0px');
          done();
        }).click();
      });
      it('position: right middle, margin: 0, modal: 450x350, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('right', 'middle', 0, 450, 350, 400, 300);
          expect(pos).not.to.have.property('bottom');
          expect(pos).to.have.property('top');
          expect(pos.top).to.equal('0px');

          expect(pos).to.have.property('right');
          expect(pos).to.have.property('left');
          expect(pos.right).to.equal('0px');
          expect(pos.left).to.equal('auto');
          done();
        }).click();
      });
      it('position: center top, margin: 0, modal: 450x350, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('center', 'top', 0, 450, 350, 400, 300);
          expect(pos).not.to.have.property('bottom');
          expect(pos).to.have.property('top');
          expect(pos.top).to.equal('0px');

          expect(pos).not.to.have.property('right');
          expect(pos).to.have.property('left');
          expect(pos.left).to.equal('0px');
          done();
        }).click();
      });
      it('position: center bottom, margin: 0, modal: 450x350, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('center', 'bottom', 0, 450, 350, 400, 300);
          expect(pos).to.have.property('bottom');
          expect(pos).to.have.property('top');
          expect(pos.bottom).to.equal('0px');
          expect(pos.top).to.equal('auto');

          expect(pos).not.to.have.property('right');
          expect(pos).to.have.property('left');
          expect(pos.left).to.equal('0px');
          done();
        }).click();
      });
      it('position: left top, margin: 0, modal: 450x350, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('left', 'top', 0, 450, 350, 400, 300);
          expect(pos).not.to.have.property('bottom');
          expect(pos).to.have.property('top');
          expect(pos.top).to.equal('0px');

          expect(pos).not.to.have.property('right');
          expect(pos).to.have.property('left');
          expect(pos.left).to.equal('0px');
          done();
        }).click();
      });
      it('position: left bottom, margin: 0, modal: 450x350, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('left', 'bottom', 0, 450, 350, 400, 300);
          expect(pos).to.have.property('bottom');
          expect(pos).to.have.property('top');
          expect(pos.bottom).to.equal('0px');
          expect(pos.top).to.equal('auto');

          expect(pos).not.to.have.property('right');
          expect(pos).to.have.property('left');
          expect(pos.left).to.equal('0px');
          done();
        }).click();
      });
      it('position: right top, margin: 0, modal: 450x350, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('right', 'top', 0, 450, 350, 400, 300);
          expect(pos).not.to.have.property('bottom');
          expect(pos).to.have.property('top');
          expect(pos.top).to.equal('0px');

          expect(pos).to.have.property('right');
          expect(pos).to.have.property('left');
          expect(pos.right).to.equal('0px');
          expect(pos.left).to.equal('auto');
          done();
        }).click();
      });
      it('position: right bottom, margin: 0, modal: 450x350, wrapper: 400x300', function(done) {
        $('<a href="#"/>').patPloneModal().on('show.plone-modal.patterns', function(e) {
          var modal = $(this).data('pattern-plone-modal');
          var pos = modal.findPosition('right', 'bottom', 0, 450, 350, 400, 300);
          expect(pos).to.have.property('bottom');
          expect(pos).to.have.property('top');
          expect(pos.bottom).to.equal('0px');
          expect(pos.top).to.equal('auto');

          expect(pos).to.have.property('right');
          expect(pos).to.have.property('left');
          expect(pos.right).to.equal('0px');
          expect(pos.left).to.equal('auto');
          done();
        }).click();
      });
    });
  });

});
