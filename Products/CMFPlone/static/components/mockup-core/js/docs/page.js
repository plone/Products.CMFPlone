define([
  'jquery',
  'underscore',
  'backbone',
  'marked',
  'react',
  'mockup-docs-pattern'
], function($, _, Backbone, marked, React, pattern) {
  'use strict';

  var div = React.DOM.div,
      a = React.DOM.a,
      p = React.DOM.p,
      h1 = React.DOM.h1,
      h2 = React.DOM.h2,
      li = React.DOM.li,
      ul = React.DOM.ul;

  var Page = React.createClass({
    getDefaultProps: function() {
      return {
        title: '',
        description: '',
        autotoc: true,
        text: ''
      };
    },
    componentDidUpdate: function() {
      var currentPage = Backbone.history.location.hash.substr(1).split('/');
      if (currentPage.length > 1) {
        $(window).scrollTop($('#' + currentPage[1]).offset().top - $('.mockup-header').outerHeight(true));
      }
    },
    render: function() {
      var page = this.props, PageText, PageContent, patternID;

      if (typeof page.text === 'string' && page.text.trim().substr(0, 1) !== '<') {
        PageText = marked(page.text);
      } else {
        PageText = page.text;
      }

      if (page.autotoc) {
        var autotoc = [], autotocID,
            $autotoc = $('<div>' + PageText + '</div>');

        $autotoc.find('h1,h2').each(function(i) {
          autotocID = 'mockup-autotoc_' + i;
          $(this).attr('id', autotocID);
          if ($.nodeName(this, 'h1')) {
            autotoc.push({
              id: autotocID,
              title: $(this).text(),
              submenu: []
            });
          } else {
            autotoc[autotoc.length - 1].submenu.push({
              id: autotocID,
              title: $(this).text()
            });
          }
        });
        PageContent =
          div({ className: 'row' }, [
            div({ className: 'col-md-3' }, [
              div({ className: 'mockup-autotoc hidden-print', role: 'complementary' }, [
                ul({ className: 'nav' },
                  autotoc.map(function(item) {
                    return (
                      li({ key: page.id + '/' + item.id }, [
                        a({ href: '#' + page.id + '/' + item.id }, item.title),
                        item.submenu ?
                          ul({ className: 'nav' },
                            item.submenu.map(function(subitem) {
                              return (
                                li({ key: page.id + '/' + subitem.id },
                                  a({ href: '#' + page.id + '/' + subitem.id }, subitem.title)
                                )
                              );
                            })
                          ) : undefined
                      ])
                    );
                  })
                )
              ])
            ]),
            div({ className: 'col-md-9', dangerouslySetInnerHTML: {__html: $autotoc.html()} })
          ]);
      } else if (page.patterns) {
        if (Backbone.history.location.hash.substr(1).split('/').length > 1) {
          patternID = Backbone.history.location.hash.substr(1).split('/')[1];
        }

        PageContent =
          div({ className: 'row mockup-patterns' },
            page.patterns.map(function(_pattern) {
              return (
                div({}, [
                  div({ key: _pattern.id, id: _pattern.id, className: 'col-xs-12 col-sm-4 col-md-3' },
                    a({
                      className: patternID === _pattern.id ? 'mockup-pattern-tile active' : 'mockup-pattern-tile',
                      href: '#' + page.id + '/' + _pattern.id
                    }, [
                      h2({}, _pattern.title),
                      p({}, _pattern.description)
                    ])
                  ),
                  patternID === _pattern.id ? pattern(_pattern) : ''
                ])
              );
            })
          );

      } else if (typeof PageText === 'string') {
        PageContent = div({ dangerouslySetInnerHTML: {__html: PageText} });
      }

      return  (
        div({ className: 'mockup-content', id: 'content' }, [
          div({ className: 'page-header' },
            div({ className: 'container' }, [
              h1({}, page.title),
              p({}, page.description)
            ])
          ),
          div({ className: 'container' },
            div({ key: page.id, className: 'page-content' }, PageContent)
          )
        ])
      );
    }
  });

  return Page;
});
