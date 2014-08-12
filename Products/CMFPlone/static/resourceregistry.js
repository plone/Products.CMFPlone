/* globals less:true, domready:true */

(function() {
  'use strict';

  require(['jquery'], function($){
    $(document).ready(function() {
      require(['++resource++mockup/resourceregistry/pattern.js', 'mockup-registry'], function(ResourceRegistry, Registry){
        Registry.scan($('.pat-resourceregistry'));
      });
    });
  });

}());