if (window.jQuery) {
  define( 'jquery', [], function () {
    'use strict';
    return window.jQuery;
  } );
}

define([
  'jquery',
  'pat-registry',
  'mockup-patterns-base',
  'mockup-patterns-modal',
  'mockup-patterns-structure'
], function($, registry, Base, Modal, Structure) {
  'use strict';

  $(document).ready(function() {
    var $structure = $('.pat-structure');
    if ($structure.length === 1) {
      var $container = $structure.parents('#content');
      if ($container.length === 0) {
        // uh oh, no content id, let's go up a few levels and use that as parent
        $container = $structure.parent().parent();
      }
      var $modal = $container.patPloneModal({
        position: 'middle top',
        width: '95%',
        title: 'Folder Contents',
        backdropOptions: {
          closeOnEsc: false,
          closeOnClick: false
        }
      });
      var modal = $modal.data('pattern-plone-modal');
      modal.show();
      modal.$modal.find('a.close').on('destroy.plone-modal.patterns', function() {
        var $base = $('base');
        var url;
        if ($base.length === 0) {
          url = window.location.href.replace('@@folder_contents', '').replace('folder_contents', '');
        } else {
          url = $base.attr('href');
        }
        window.location = url;
      });
    }
  });

  return {};
});
