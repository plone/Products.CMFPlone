/* global module:true, process:true */

(function() {
  'use strict';

  var fs = require('fs'),
      less = require('less'),
      extend = require('extend'),
      path = require('path'),
      appDir = process.cwd(),
      karmaConstants = require(appDir + '/node_modules/karma/lib/constants'),
      MockupGrunt = function (requirejsOptions) { this.init(requirejsOptions); },
      BROWSERS = process.env.BROWSERS;

  if (BROWSERS) {
    BROWSERS = BROWSERS.split(',');
  } else {
    BROWSERS = [ 'SL_Chrome', 'SL_Firefox' ];
  }

  MockupGrunt.prototype = {

    sections: {
      requirejs: {
        registerBundle: function(name, customGruntConfig, bundleOptions, sections) {
          this.gruntConfig.requirejs = this.gruntConfig.requirejs || {};
          this.gruntConfig.requirejs[name] = this.gruntConfig.requirejs[name] || {};
          this.gruntConfig.requirejs[name].options = this.gruntConfig.requirejs[name].options || {};

          this.gruntConfig.requirejs[name].options = {
            name: 'node_modules/requirejs/require.js',
            include: ['mockup-bundles-' + name].concat(bundleOptions.extraInclude || []),
            exclude: bundleOptions.exclude || [],
            insertRequire: ['mockup-bundles-' + name],
            out: bundleOptions.path + name + '.js'
          };
        }
      },
      uglify: {
        registerBundle: function(name, customGruntConfig, bundleOptions, sections) {
          this.gruntConfig.uglify = this.gruntConfig.uglify || {};
          this.gruntConfig.uglify[name] = this.gruntConfig.uglify[name] || {};
          this.gruntConfig.uglify[name].files = this.gruntConfig.uglify[name].files || {};
          this.gruntConfig.uglify[name].options = {
            mangle: false,
            sourceMap: true,
            sourceMapName: bundleOptions.path + name + '.min.js.map'
          };
          this.gruntConfig.uglify[name].files[bundleOptions.path + name + '.min.js'] = [
            bundleOptions.path + name + '.js'
          ];
        }
      },
      less: {
        registerBundle: function(name, customGruntConfig, bundleOptions, sections) {
          var gruntConfig = this.gruntConfig;

          gruntConfig.less = gruntConfig.less || {};
          gruntConfig.less[name] = gruntConfig.less[name] || {};
          gruntConfig.less[name].files = gruntConfig.less[name].files || {};
          gruntConfig.less[name].files[bundleOptions.path + name + '.min.css'] = 'less/' + name + '.less';
          gruntConfig.less[name].options = {
            sourceMap: true,
            sourceMapFilename: bundleOptions.path + name + '.min.css.map'
          };

          gruntConfig.watch = gruntConfig.watch || {};
          gruntConfig.watch['less-' + name] = gruntConfig.watch['less-' + name] || {
            files: [ 'less/' + name + '.less' ],
            tasks: [ 'less:' + name ]
          };

          var parser = new(less.Parser)({ syncImport: true, paths: ['less'], filename: name + '.less' }),
              bundleFile = fs.readFileSync('less/' + name + '.less', { encoding: 'utf-8' });

          parser.parse(bundleFile, function() {
            for(var file in parser.imports.files) {
              gruntConfig.watch['less-' + name].files.push(file);
            }
          });
        }
      },
      copy: {
        registerBundle: function(name, customGruntConfig, bundleOptions, sections) {
          this.gruntConfig.copy = this.gruntConfig.copy || {};
          this.gruntConfig.copy[name] = this.gruntConfig.copy[name] || {};
          this.gruntConfig.copy[name].files = this.gruntConfig.copy[name].files || [];
          this.gruntConfig.copy[name].files = this.gruntConfig.copy[name].files.concat([
            // BOOTSTRAP
            { expand: true, cwd: 'bower_components/bootstrap/dist/fonts/', src: 'glyphicons-halflings-regular.*', dest: bundleOptions.path,
              rename: function(dest, src) { return dest + name + '-bootstrap-' + src; }},
            // TINYMCE
            { expand: true, cwd: 'bower_components/tinymce-builded/js/tinymce/langs', src: '*', dest: bundleOptions.path + name + '-tinymce/langs'},
            { expand: true, cwd: 'bower_components/tinymce-builded/js/tinymce/skins/lightgray/fonts/', src: 'tinymce*', dest: bundleOptions.path,
              rename: function(dest, src) { return dest + name + '-tinymce-font-' + src; }},
            { expand: true, cwd: 'bower_components/tinymce-builded/js/tinymce/skins/lightgray/img/', src: '*', dest: bundleOptions.path,
              rename: function(dest, src) { return dest + name + '-tinymce-img-' + src; }},
            { expand: true, cwd: 'bower_components/tinymce-builded/js/tinymce/skins/lightgray/', src: 'content.min.css', dest: bundleOptions.path,
              rename: function(dest, src) { return dest + name + '-tinymce-' + src; }},
            // JQTREE
            { expand: true, cwd: 'bower_components/jqtree/', src: 'jqtree-circle.png', dest: bundleOptions.path,
              rename: function(dest, src) { return dest + name + '-jqtree-' + src; }},
            // SELECT2
            { expand: true, cwd: 'bower_components/select2/', src: 'select2*.png', dest: bundleOptions.path,
              rename: function(dest, src) { return dest + name + '-select2-' + src; }},
            { expand: true, cwd: 'bower_components/select2/', src: 'select2*.gif', dest: bundleOptions.path,
              rename: function(dest, src) { return dest + name + '-select2-' + src; }},
          ]);
        }
      },
      sed: {
        registerBundle: function(name, customGruntConfig, bundleOptions, sections) {
          this.gruntConfig.sed = this.gruntConfig.sed || {};
          // source maps
          this.gruntConfig.sed[name + '.min.css.map'] = {
            path: bundleOptions.path + name + '.min.css',
            pattern: 'sourceMappingURL=' + bundleOptions.path + name + '.min.css.map',
            replacement: 'sourceMappingURL=' + bundleOptions.url + '.min.css.map',
          };
          this.gruntConfig.sed[name + '.min.js.map'] = {
            path: bundleOptions.path + name + '.min.js',
            pattern: 'sourceMappingURL=' + name + '.min.js.map',
            replacement: 'sourceMappingURL=' + bundleOptions.url + '.min.js.map',
          };
          // pattern resources
          // BOOTSTRAP
          this.gruntConfig.sed[name + '-bootstrap-glyphicons'] = {
            path: bundleOptions.path + name + '.min.css',
            pattern: 'url\\(\'../bower_components/bootstrap/dist/fonts/glyphicons-halflings-regular',
            replacement: 'url(\'' + bundleOptions.url + '-bootstrap-glyphicons-halflings-regular'
          };
          // TINYMCE
          this.gruntConfig.sed[name + '-tinymce-fonts'] = {
            path: bundleOptions.path + name + '.min.css',
            pattern: 'url\\((\'?)fonts/tinymce',  // match urls with and without quotes
            replacement: 'url($1' + bundleOptions.url + '-tinymce-font-tinymce'
          };
          this.gruntConfig.sed[name + '-tinymce-img-loader'] = {
            path: bundleOptions.path + name + '.min.css',
            pattern: 'url\\(\'?img/loader.gif\'?',  // match urls with and without quotes
            replacement: 'url(\'' + bundleOptions.url + '-tinymce-img-loader.gif\''
          };
          this.gruntConfig.sed[name + '-tinymce-img-anchor'] = {
            path: bundleOptions.path + name + '.min.css',
            pattern: 'url\\(\'?img/anchor.gif\'?',
            replacement: 'url(\'' + bundleOptions.url + '-tinymce-img-anchor.gif\''
          };
          this.gruntConfig.sed[name + '-tinymce-img-object'] = {
            path: bundleOptions.path + name + '.min.css',
            pattern: 'url\\(\'?img/object.gif\'?',
            replacement: 'url(\'' + bundleOptions.url + '-tinymce-img-object.gif\''
          };
          // TINYMCE content.min
          this.gruntConfig.sed[name + '-tinymce-content.min.css'] = {
            // replace default content.min.css
            path: bundleOptions.path,
            recursive: true,
            pattern: '../../../bower_components/tinymce-builded/js/tinymce/skins/lightgray/content.min.css',
            replacement: bundleOptions.url + '-tinymce-content.min.css'
          };
          this.gruntConfig.sed[name + '-tinymce-fonts2'] = {
            path: bundleOptions.path + name + '-tinymce-content.min.css',
            pattern: 'url\\((\'?)fonts/tinymce',  // match urls with and without quotes
            replacement: 'url($1' + bundleOptions.url + '-tinymce-font-tinymce'
          };
          this.gruntConfig.sed[name + '-tinymce-img-loader2'] = {
            path: bundleOptions.path + name + '-tinymce-content.min.css',
            pattern: 'url\\(\'?img/loader.gif\'?',
            replacement: 'url(\'' + bundleOptions.url + '-tinymce-img-loader.gif\''
          };
          this.gruntConfig.sed[name + '-tinymce-img-anchor2'] = {
            path: bundleOptions.path + name + '-tinymce-content.min.css',
            pattern: 'url\\(\'?img/anchor.gif\'?',
            replacement: 'url(\'' + bundleOptions.url + '-tinymce-img-anchor.gif\''
          };
          this.gruntConfig.sed[name + '-tinymce-img-object2'] = {
            path: bundleOptions.path + name + '-tinymce-content.min.css',
            pattern: 'url\\(\'?img/object.gif\'?',
            replacement: 'url(\'' + bundleOptions.url + '-tinymce-img-object.gif\''
          };
          // SELECT2
          this.gruntConfig.sed[name + '-select2-images'] = {
            path: bundleOptions.path + name + '.min.css',
            pattern: 'url\\(\'select2',
            replacement: 'url(\'' + bundleOptions.url + '-select2-select2'
          };
          // JQTREE
          this.gruntConfig.sed[name + '-jqtree-circle'] = {
            path: bundleOptions.path + name + '.min.css',
            pattern: 'url\\(jqtree-circle.png',
            replacement: 'url(\'' + bundleOptions.url + '-jqtree-jqtree-circle.png\''
          };
        }
      }

    },
    init: function(requirejsOptions) {
      this.requirejsOptions = requirejsOptions;
      this.patterns = [];
      this.bundles = {};
      this.gruntConfig = {};
      this.files = [
        /*
        * include initial framework (mocha and requirejs) with html5
        * shims/shams/polyfills
        */
        'bower_components/selectivizr/selectivizr.js',
        'bower_components/es5-shim/es5-shim.js',
        'bower_components/es5-shim/es5-sham.js',
        'bower_components/console-polyfill/index.js',
        'node_modules/mocha/mocha.js',
        'node_modules/karma-mocha/lib/adapter.js',
        'node_modules/requirejs/require.js',
        'node_modules/karma-requirejs/lib/adapter.js',

        /*
        * include requirejs configuration
        */
        'js/config.js',

        /*
        * include karma requirejs configuration
        */
        'tests/config.js',
      ];

      /*
      * provide (but not include) all scripts defined in requirejs's
      * configuration
      *
      * also at the same time create a list of all patterns to be loaded with
      * docs bundle
      */
      var path;
      for (var key in this.requirejsOptions.paths) {
        path = this.requirejsOptions.paths[key];
        if (path.indexOf('.md') !== path.length - 3) {
          this.files.push({ pattern: path + '.js', included: false });
        }
        if (key.indexOf('mockup-patterns-') === 0) {
          this.patterns.push(key);
        }
      }

      /*
      * provide (but not include) all files in "tests/" and "js/" folder
      * those files will be loaded by requirejs at later points
      *
      * TODO: simplify the pattern to include everything inside js/ and
      * tests/ folders.
      */
      this.files = this.files.concat([
        {pattern: 'tests/**/*', included: false},
        {pattern: 'js/**/*', included: false},
        {pattern: 'patterns/**/*', included: false}
      ]);


    },
    registerBundle: function(name, customGruntConfig, bundleOptions, sections) {

      /*
       * TODO: add description
       */
      extend(true, this.gruntConfig, customGruntConfig || {});

      /*
       * TODO: add description
       */
      bundleOptions = extend(true, {
        path: 'build/',
        url: '++resource++plone.app.' + name,
        insertExtraRequires: []
      }, bundleOptions || {});

      /*
       * TODO: add description
       */
      sections = sections || ['requirejs', 'uglify', 'less', 'copy', 'sed'];

      /*
       * TODO: add description
       */
      for (var i = 0; i < sections.length; i = i + 1) {
        if (this.sections[sections[i]]) {
          this.sections[sections[i]].registerBundle.apply(
            this,
            [ name, customGruntConfig, bundleOptions, sections ]
          );
        }
      }

      /*
       * TODO: add description
       */
      var bundleTasks = [];
      for (var j = 0; j < sections.length; j = j + 1) {
        if (this.gruntConfig[sections[j]][name] !== {} && sections[j] !== 'sed') {
          bundleTasks.push(sections[j] + ':' + name);
        } else if (sections[j] === 'sed') {
          for (var sedSection in this.gruntConfig.sed) {
            if (this.gruntConfig.sed.hasOwnProperty(sedSection) && sedSection.indexOf(name) === 0) {
              bundleTasks.push('sed:' + sedSection);
            }
          }
        }
      }
      this.bundles[name] = bundleTasks;
    },
    initGrunt: function(grunt, customGruntConfig) {
      extend(true, this.gruntConfig, customGruntConfig || {});

      /*
       * Register different test runners
       */
      var bundles = [];
      for (var name in this.bundles) {
        bundles.push('bundle-' + name);
        grunt.registerTask('bundle-' + name, this.bundles[name]);
      }
      grunt.registerTask('test', [ 'jshint', 'karma:test' ]);
      grunt.registerTask('test_once', [ 'jshint', 'karma:testOnce' ]);
      grunt.registerTask('test_jenkins', [ 'jshint', 'karma:testJenkins' ]);
      grunt.registerTask('test_dev', [ 'karma:testDev' ]);
      grunt.registerTask('test_serve', [ 'karma:testServe' ]);
      grunt.registerTask('test_ci', [ 'jshint', 'karma:testCI'].concat(bundles));

      /*
       * TODO: add description
       */
      grunt.initConfig(extend(true, {
        jshint: { options: { jshintrc: '.jshintrc' }, all: ['Gruntfile.js', 'js/**/*.js', 'tests/*.js'] },
        karma: {
          options: {
            basePath: './',
            frameworks: ['mocha', 'chai'],
            files: this.files,
            preprocessors: { 'js/**/*.js': 'coverage' },
            reporters: ['dots', 'progress', 'coverage', 'spec'],
            coverageReporter: { type : 'lcov', dir : 'coverage/' },
            port: 9876,
            colors: true,
            // logLevel: karmaConstants.LOG_DEBUG,
            logLevel: karmaConstants.LOG_INFO,
            browserNoActivityTimeout: 200000,
            autoWatch: true,
            captureTimeout: 60000,
            plugins: [
              'karma-mocha',
              'karma-chai',
              'karma-coverage',
              'karma-requirejs',
              'karma-sauce-launcher',
              'karma-chrome-launcher',
              'karma-phantomjs-launcher',
              'karma-junit-reporter',
              'karma-spec-reporter'

            ]
          },
          test: {
            browsers: ['PhantomJS']
          },
          testOnce: {
            singleRun: true,
            browsers: ['PhantomJS']
          },
          testJenkins: {
            autoWatch: false,
            colors: false,
            singleRun: true,
            browsers: ['PhantomJS'],
            reporters: ['junit'],
            junitReporter: {
              outputFile: 'test-results.xml'
            },
          },
          testDev: {
            browsers: ['Chrome'],
            preprocessors: {},
            reporters: ['dots', 'progress'],
            plugins: [
              'karma-mocha',
              'karma-chai',
              'karma-requirejs',
              'karma-chrome-launcher'
            ]
          },
          testServe: {
            preprocessors: {},
            reporters: ['dots', 'progress'],
            plugins: [
              'karma-mocha',
              'karma-chai',
              'karma-requirejs'
            ]
          },
          testCI: {
            singleRun: true,
            port: 8080,
            recordVideo: true,
            reporters: ['junit', 'coverage', 'saucelabs'],
            junitReporter: { outputFile: 'test-results.xml' },
            sauceLabs: { testName: 'Mockup', startConnect: true },
            browsers: BROWSERS,
            customLaunchers: {
              'SL_Chrome': { base: 'SauceLabs', browserName: 'chrome', platform: 'Windows 8.1', version: '38' },
              'SL_Firefox': { base: 'SauceLabs', browserName: 'firefox', platform: 'Windows 8.1', version: '33' },
              'SL_Opera': { base: 'SauceLabs', browserName: 'opera', platform: 'Windows 8.1', version: '25' },
              'SL_Safari': { base: 'SauceLabs', browserName: 'safari', platform: 'Mac 10.9', version: '7.1' },
              'SL_IE_8': { base: 'SauceLabs', browserName: 'internet explorer', platform: 'Windows 7', version: '8' },
              'SL_IE_9': { base: 'SauceLabs', browserName: 'internet explorer', platform: 'Windows 7', version: '9' },
              'SL_IE_10': { base: 'SauceLabs', browserName: 'internet explorer', platform: 'Windows 7', version: '10' },
              'SL_IE_11': { base: 'SauceLabs', browserName: 'internet explorer', platform: 'Windows 8.1', version: '11' },
              'SL_IPhone': { base: 'SauceLabs', browserName: 'iphone', platform: 'OS X 10.9', version: '7.1' },
              'SL_IPad': { base: 'SauceLabs', browserName: 'ipad', platform: 'OS X 10.9', version: '7.1' },
              'SL_Android': { base: 'SauceLabs', browserName: 'android', platform: 'Linux', version: '4.3' }
            }
          }
        },
        requirejs: {
          options: this.requirejsOptions
        },
        less: {
          options: {
            compress: true,
            cleancss: false,
            ieCompat: true,
            paths: ['less']
          }
        },
        sed: {
          'bootstrap': {
            path: 'node_modules/lcov-result-merger/index.js',
            pattern: 'throw new Error\\(\'Unknown Prefix ',
            replacement: '//throw// new Error(\'Unknown Prefix '
          }
        }
      }, this.gruntConfig));

      /*
       * TODO: add description
       */
      grunt.loadNpmTasks('grunt-contrib-copy');
      grunt.loadNpmTasks('grunt-contrib-jshint');
      grunt.loadNpmTasks('grunt-contrib-less');
      grunt.loadNpmTasks('grunt-contrib-requirejs');
      grunt.loadNpmTasks('grunt-contrib-uglify');
      grunt.loadNpmTasks('grunt-contrib-watch');
      grunt.loadNpmTasks('grunt-karma');
      grunt.loadNpmTasks('grunt-sed');
    }
  };
  module.exports = MockupGrunt;
})();
