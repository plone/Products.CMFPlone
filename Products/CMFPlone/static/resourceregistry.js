/* globals requirejs */

(function() {
  'use strict';

  require(['jquery'], function($){
    $(document).ready(function() {
      requirejs.config({
        paths: {
          'mockup-patterns-resourceregistry-url': '++resource++mockup/resourceregistry'
        }
      });
      require(['++resource++mockup/resourceregistry/pattern.js', 'pat-registry'], function(ResourceRegistry, Registry){
        Registry.scan($('.pat-resourceregistry'));
      });
    });
  });

}());