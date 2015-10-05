define([
  'underscore',
  'marked',
  'react',
  'pat-registry'
], function(_, marked, React, Registry) {
  'use strict';

  var div = React.DOM.div,
      a = React.DOM.a,
      h2 = React.DOM.h2,
      tr = React.DOM.tr,
      th = React.DOM.th,
      td = React.DOM.td,
      tbody = React.DOM.tbody,
      thead = React.DOM.thead,
      table = React.DOM.table;

  var Pattern = React.createClass({
    getDefaultProps: function() {
      return {
        id: '',
        url: ''
      };
    },
    getInitialState: function() {
      return {pattern: undefined};
    },
    parsePattern: function(text) {
      var option = /(.*)\((.*)\): (.*) \((.*)\)$/,
          section = /^Options:|^Documentation:|^License:|^Example:/,
          currentOption,
          currentExample,
          currentSection,
          examples = {},
          pattern = {};

      text = text.substring(1, text.length - 1);
      _.each(text.split('\n'), function(line, lineNumber) {
        line = line.substring(line.indexOf('*') + 2).replace('\r', '');

        if (section.exec(line) !== null) {
          currentSection = section.exec(line)[0].toLowerCase();
          currentSection = currentSection.substring(0, currentSection.length - 1);
          if (currentSection === 'example') {
            currentExample = line.substring(8).trim();
          }
        } else if (currentSection) {
          if (currentSection === 'options') {
            currentOption = option.exec(line);
            if (currentOption) {
              if (!pattern.options) {
                pattern.options = {};
              }
              pattern.options[currentOption[1].trim()] = {
                type: currentOption[2].trim(),
                description: currentOption[3].trim(),
                defaultValue: currentOption[4].trim()
              };
            }
          } else if (currentExample && currentSection === 'example') {
            if (!examples[currentExample]) {
              examples[currentExample] = '';
            }
            examples[currentExample] += line + '\n';
          } else {
            if (!pattern[currentSection]) {
              pattern[currentSection] = '';
            }
            pattern[currentSection] += line + '\n';
          }
        }
      });
      _.each(pattern, function(value, i) {
        if (typeof value === 'string') {
          pattern[i] = '';
          var lines = value.split('\n'),
          firstLineSpaces = lines[0].length - lines[0].replace(/^\s+/,'').length;
          _.each(value.split('\n'), function(line, j) {
            pattern[i] += line.substring(firstLineSpaces) + '\n';
          });

          pattern[i] = marked(pattern[i]);

          _.each(examples, function(example, name) {
            example = '' +
              '<div class="mockup-pattern-example">' + example +
              '<p><pre>' + _.escape(example) + '</pre><p>' +
              '</div>';
            pattern[i] = pattern[i].replace('{{ ' + name + ' }}', example);
          });

        }
      });
      return pattern;
    },
    componentWillMount: function() {
      var self = this;
      if (this.props.url) {
        require([
          'text!' + this.props.url, 'mockup-patterns-' + this.props.id
        ], function (pattern) {
          pattern = (/\/\*[\s\S]*?\*\//gm).exec(pattern)[0];
          self.setState({pattern: self.parsePattern(pattern)});
        });
      }
    },
    componentDidUpdate: function() {
      Registry.scan(this.getDOMNode());
    },
    render: function() {
      if (!this.state.pattern) {
        return div({ className: 'mockup-pattern' });
      }
      var documentation = this.state.pattern.documentation,
          options = this.state.pattern.options,
          license = this.state.pattern.license;

      var render_options = [];
      if (options) {
        render_options = [
          h2({}, 'Configuration'),
          div({ className: 'table-responsive mockup-pattern-configuration' },
            table({ className: 'table table-stripped table-condensed' }, [
              thead({},
                tr({}, [
                  th({}, 'Option'),
                  th({}, 'Type'),
                  th({}, 'Default'),
                  th({}, 'Description')
                ])
              ),
              tbody({},
                Object.keys(options).map(function(name) {
                  return (
                    tr({ key: name }, [
                      td({}, name),
                      td({}, options[name].type),
                      td({}, options[name].defaultValue),
                      td({}, options[name].description)
                    ])
                  );
                })
              )
            ])
          )
        ];
      }

      var render_license = [];
      if (license) {
        render_license = [
          h2({}, 'License'),
          div({ className: 'mockup-pattern-license', dangerouslySetInnerHTML: {__html: license} })
        ];
      }

      return (
        div({ className: 'mockup-pattern' }, [
          h2({}, 'Documentation'),
          div({ className: 'mockup-pattern-documentation', dangerouslySetInnerHTML: {__html: documentation} })
        ].concat(render_options).concat(render_license))
      );
    }
  });

  return Pattern;
});
