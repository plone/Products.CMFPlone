define([
  'jquery',
  'pat-registry',
  'mockup-patterns-resourceregistry',
], function($, registry, resource_registry) {
  'use strict';
  if (!registry.initialized) {
    registry.init();
  }
});
