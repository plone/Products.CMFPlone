// tests for Base
//
// @author Rok Garbas
// @version 1.0
// @licstart  The following is the entire license notice for the JavaScript
//            code in this page.
//
// Copyright (C) 2010 Plone Foundation
//
// This program is free software; you can redistribute it and/or modify it
// under the terms of the GNU General Public License as published by the Free
// Software Foundation; either version 2 of the License.
//
// This program is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
// FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
// more details.
//
// You should have received a copy of the GNU General Public License along with
// this program; if not, write to the Free Software Foundation, Inc., 51
// Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
//
// @licend  The above is the entire license notice for the JavaScript code in
//          this page.
//

define([
  'expect',
  'jquery',
  'mockup-registry',
  'mockup-patterns-base'
], function(expect, $, Registry, Base) {
  'use strict';

  window.mocha.setup('bdd');

  describe('Base', function () {

    beforeEach(function() {
      this._patterns = $.extend({}, Registry.patterns);
    });

    afterEach(function() {
      Registry.patterns = this._patterns;
    });

    it('can be extended and used in similar way as classes', function(done) {
      var Tmp = Base.extend({
        some: 'thing',
        init: function() {
          expect(this.$el).to.equal('element');
          expect(this.options).to.have.keys(['option']);
          this.extra();
        },
        extra: function() {
          expect(this.some).to.equal('thing');
          done();
        }
      });
      var tmp = new Tmp('element', {option: 'value'});
    });

    it('can be extended multiple times', function(done) {
      var Tmp1 = Base.extend({
        some: 'thing1',
        something: 'else',
        init: function() {
          expect(this.some).to.equal('thing3');
          expect(this.something).to.equal('else');
          done();
        }
      });
      var Tmp2 = Tmp1.extend({
        some: 'thing2',
        init: function() {
          expect(this.some).to.equal('thing3');
          expect(this.something).to.equal('else');
          this.constructor.__super__.constructor.__super__.init.call(this);
        }
      });
      var Tmp3 = Tmp2.extend({
        some: 'thing3',
        init: function() {
          expect(this.some).to.equal('thing3');
          expect(this.something).to.equal('else');
          this.constructor.__super__.init.call(this);
        }
      });
      var tmp3 = new Tmp3('element', {option: 'value'});
    });

    it('can also extend with already existing constructors', function(done) {
      var Tmp1 = function() {
        expect(1).to.be(1);
        done();
      };
      var Tmp2 = function() {};
      Tmp2.constructor = Tmp1;
      new Base.extend(Tmp2)('element');
    });

    it('has on/trigger helpers to prefix events', function(done) {
      var Tmp = Base.extend({
        name: 'tmp',
        init: function() {
          this.on('something', function(e, arg1) {
            expect(arg1).to.be('yaay!');
            done();
          });
          this.trigger('somethingelse', ['yaay!']);
        }
      });
      var tmp = new Tmp(
        $('<div/>').on('somethingelse.tmp.patterns', function(e, arg1) {
          $(this).trigger('something.tmp.patterns', [arg1]);
          done();
        }));
    });

  });

});
