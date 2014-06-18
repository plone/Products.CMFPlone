/* globals module:true */

module.exports = function(grunt) {
  'use strict';

  var MockupGrunt = require('./js/grunt'),
      requirejsOptions = require('./js/config'),
      mockup = new MockupGrunt(requirejsOptions);

  mockup.initGrunt(grunt);

};
