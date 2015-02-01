define([
  'underscore',
  'react',
  'mockup-docs-navigation',
  'mockup-docs-page',
  'bootstrap-collapse',
  'bootstrap-transition'
], function(_, React, navigation, page) {
  'use strict';

  var div = React.DOM.div,
      a = React.DOM.a,
      p = React.DOM.p,
      li = React.DOM.li,
      ul = React.DOM.ul,
      nav = React.DOM.nav,
      span = React.DOM.span,
      button = React.DOM.button,
      iframe = React.DOM.iframe,
      header = React.DOM.header,
      footer = React.DOM.footer;

  var AppView = React.createClass({
    propTypes: {
      pages: React.PropTypes.array
    },
    getDefaultProps: function() {
      var self = this;
      return {
        defaultPage: 'index',
        pages: []
      };
    },
    getInitialState: function() {
      return {
        page: 'index'
      };
    },
    render: function() {
      var pageID = this.state.page.split('/')[0],
          CurrentPage = page(_.findWhere(this.props.pages, {id: pageID}));
      return (
        div({ className: 'wrapper page-' + pageID }, [
          a({ href: '#content', className: 'sr-only' }, 'Skip to main content' ),
          header({ className: 'navbar navbar-inverse navbar-fixed-top mockup-header' },
            div({ className: 'header container' }, [
              div({ className: 'navbar-header' }, [
                button({ type: 'button', className: 'navbar-toggle', 'data-toggle': 'collapse', 'data-target': '#navigation' }, [
                  span({ className: 'sr-only' }, 'Toggle navigation'),
                  span({ className: 'icon0bar' }, ''),
                  span({ className: 'icon0bar' }, ''),
                  span({ className: 'icon0bar' }, '')
                ]),
                a({ className: 'navbar-brand', href: '#' }, 'Mockup')
              ]),
              nav({ className: 'collapse navbar-collapse', id: 'navigation'}, [
                this.transferPropsTo(navigation()),
                this.transferPropsTo(navigation({ position: 'right' }))
              ])
            ])
          ),
          CurrentPage,
          footer({ className: 'navbar navbar-inverse mockup-footer' },
            div({ className: 'container' }, [
              div({ className: 'row' }, [
                div({ className: 'col-xs-12 col-sm-6 mockup-credits' }, [
                  p({}, ['Built by ', a({ href: 'http://plone.org' }, 'Plone'),' community.']),
                  p({}, ['Code and documentation licensed under ', a({ href: 'http://opensource.org/licenses/BSD-3-Clause' }, 'BSD'),'.']),
                ]),
                div({ className: 'col-xs-12 col-sm-6' },
                  ul({ className: 'mockup-links' }, [
                    li({}, a({ href: 'https://github.com/plone/mockup/issues' }, 'Issues')),
                    li({}, a({ href: 'https://github.com/plone/mockup/releases' }, 'Releases'))
                  ])
                )
              ]),
              div({ className: 'row' },
                div({ className: 'col-xs-12 mockup-github' }, [
                  iframe({
                    src: 'http://ghbtns.com/github-btn.html?user=plone&amp;repo=mockup&amp;type=watch&amp;count=true',
                    className: 'github-btn', width: '100', height: '20', title: 'Star on GitHub'
                  }),
                  iframe({
                    src: 'http://ghbtns.com/github-btn.html?user=plone&amp;repo=mockup&amp;type=fork&amp;count=true',
                    className: 'github-btn', width: '102', height: '20', title: 'Fork on GitHub'
                  }),
                  iframe({
                    src: 'http://ghbtns.com/github-btn.html?user=plone&amp;type=follow&amp;count=true',
                    className: 'github-btn', width: '130', height: '20', title: 'Follow on GitHub'
                  })
                ])
              )
            ])
          )
        ])
      );
    }
  });

  return AppView;
});
