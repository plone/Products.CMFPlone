define([
  'jquery',
  'underscore',
  'expect',
  'sinon',
  'react',
  'mockup-registry',
  'mockup-docs-pattern'
], function($, _, expect, sinon, React, Registry, Pattern) {
  'use strict';

  window.mocha.setup('bdd');

  describe('DocsApp:Pattern', function () {

    beforeEach(function() {
      this.$root = $('<div/>');
    });

    afterEach(function() {
      React.unmountComponentAtNode(this.$root[0]);
      this.$root.remove();
    });

    it('displays documentation, options and license', function() {
      var pattern = new Pattern();
      React.renderComponent(pattern, this.$root[0]);
      expect($('.mockup-pattern', this.$root).size()).to.be(1);
      expect($('.mockup-pattern', this.$root).html()).to.be('');
      pattern.setState({
        pattern: {
          documentation: '<p>this is documentation</p>',
          license: '<p>this is license</p>',
          options: {
            option1: {
              defaultValue: 'option1 value',
              description: 'option1 description'
            },
            option2: {
              defaultValue: 'option2 value',
              description: 'option2 description'
            }
          }
        }
      });
      expect($('.mockup-pattern-documentation', this.$root).html().toLowerCase()).to.be('<p>this is documentation</p>');
      expect($('.mockup-pattern-license', this.$root).html().toLowerCase()).to.be('<p>this is license</p>');
      expect($('.mockup-pattern-configuration > table > tbody > tr', this.$root).size()).to.be(2);
    });

    it('parses first comment of pattern script', function() {
      var pattern = Pattern.componentConstructor.prototype.parsePattern('' +
        '/* Toggle pattern.\n' +
        ' *\n' +
        ' * Options:\n' +
        ' *    someoption(sometype): somedescription (somevalue)\n' +
        ' *\n' +
        ' * Documentation:\n' +
        ' *    # Example 1\n' +
        ' *\n' +
        ' *    {{ example-1 }}\n' +
        ' *\n' +
        ' * Example: example-1\n' +
        ' *    <div class="pat-somepattern" />\n' +
        ' *\n' +
        ' * License:\n' +
        ' *    Copyright (C) 2010 Plone Foundation\n' +
        ' */');
      expect(pattern).to.eql({
        documentation: '<h1 id="example-1">Example 1</h1>\n<p><div class="mockup-pattern-example">   <div class="pat-somepattern" />\n\n<p><pre>   &lt;div class=&quot;pat-somepattern&quot; /&gt;\n\n</pre><p></div></p>\n',
        license: '<p>Copyright (C) 2010 Plone Foundation</p>\n',
        options: {
          someoption: {
            type: 'sometype',
            defaultValue: 'somevalue',
            description: 'somedescription'
          }
        }
      });
    });

  });

});
