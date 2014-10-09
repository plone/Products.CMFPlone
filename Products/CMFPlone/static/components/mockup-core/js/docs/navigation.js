define([
  'underscore',
  'react',
  'backbone'
], function(_, React, Backbone) {
  'use strict';

  var ul = React.DOM.ul,
      li = React.DOM.li,
      a = React.DOM.a;

  var NavView = React.createClass({
    propTypes: {
      position: React.PropTypes.oneOf(['left', 'right'])
    },
    getDefaultProps: function() {
      return { position: 'left' };
    },
    render: function() {
      var currentPage = Backbone.history.location.hash.substr(1).split('/')[0];
      return (
        ul({ className: 'nav navbar-nav navbar-' + this.props.position },
          _.filter(this.props.pages, function(page) {
            return page.id !== this.props.defaultPage && (page.position || 'left') === this.props.position;
          }, this).map(function (page) {
            return (
              li({ key: page.id, className: currentPage === page.id ? 'active' : '' },
                a({ href: '#' + page.id, alt: page.description }, page.title)
              )
            );
          }, this)
        )
      );
    }
  });

  return NavView;
});
