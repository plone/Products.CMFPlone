// Grunt software build task definitions.
/* global module:true */
module.exports = function(grunt) {
  'use strict';

  var fs = require('fs');

  var MockupGrunt = require('./bower_components/mockup-core/js/grunt'),
      requirejsOptions = require('./js/config'),
      mockup = new MockupGrunt(requirejsOptions),
      docsExtraIncludes = [];

  for (var i = 0; i < mockup.patterns.length; i = i + 1) {
    if (mockup.patterns[i].indexOf('-url') === -1) {
      docsExtraIncludes.push(mockup.patterns[i]);
      docsExtraIncludes.push('text!' + requirejsOptions.paths[mockup.patterns[i]] + '.js');
    }
  }

  mockup.registerBundle('docs', {
    less: {
      options : {
        paths : ['../../../'],
        modifyVars : {
          bowerPath: '"bower_components/"',
          mockupPath: '"patterns/"',
          mockuplessPath: '"less/"'
        }
      }
    },
    copy: {
      docs: {
        files: [
          { expand: true, src: '*.md', dest: 'docs/dev/' },
          { expand: true, src: 'bower_components/**', dest: 'docs/dev/' },
          { expand: true, src: 'index.html', dest: 'docs/dev/' },
          { expand: true, src: 'js/**', dest: 'docs/dev/' },
          { expand: true, src: 'less/**', dest: 'docs/dev/' },
          { expand: true, src: 'lib/**', dest: 'docs/dev/' },
          { expand: true, src: 'node_modules/requirejs/require.js', dest: 'docs/dev/' },
          { expand: true, src: 'patterns/**', dest: 'docs/dev/' },
          { expand: true, src: 'tests/**', dest: 'docs/dev/' },
        ]
      },
    },
    sed: {
      'docs-css': {
        path: 'docs/dev/index.html',
        pattern: 'href="docs/dev/docs.min.css"',
        replacement: 'href="docs.min.css"'
      },
      //'docs-js': {
      //  path: 'docs/dev/index.html',
      //  pattern: '<script src="node_modules/requirejs/require.js"></script>\n  <script src="js/config.js"></script>\n  <script>\n    window.DEBUG = true;\n    require\\(\\[\'mockup-bundles-docs\'\\]\\);\n  </script>',
      //  replacement: '<script src="docs.min.js"></script>'
      //},
      'docs-legacy-js': {
        path: 'docs/dev/index.html',
        pattern: '<script src="bower_components/es5-shim/es5-shim.js"></script>\n    <script src="bower_components/es5-shim/es5-sham.js"></script>\n    <script src="bower_components/console-polyfill/index.js"></script>',
        replacement: '<script src="docs-legacy.js"></script>'
      },
      'docs-catalogurl': {
        path: 'docs/dev/index.html',
        pattern: 'data-i18ncatalogurl="/tests/json/i18n.json"',
        replacement: 'data-i18ncatalogurl="/mockup/dev/tests/json/i18n.json"',
      }
    },
  }, {
    path: 'docs/dev/',
    url: 'docs',
    extraInclude: docsExtraIncludes,
  }, ['requirejs', 'uglify', 'less', 'copy', 'sed']);

  mockup.registerBundle('structure', {}, { url: '++resource++wildcard.foldercontents-structure' });
  mockup.registerBundle('filemanager', {}, { url: '++resource++plone.resourceeditor-filemanager' });
  mockup.registerBundle('resourceregistry');
  mockup.registerBundle('plone', {}, { path: 'build/', url: '++resource++plone' });
  mockup.registerBundle('widgets', {}, { path: 'build/', url: '++resource++plone.app.widgets' });

  mockup.initGrunt(grunt, {
    sed: {
      bootstrap: {
        path: '../node_modules/lcov-result-merger/index.js',
        pattern: 'throw new Error\\(\'Unknown Prefix ',
        replacement: '//throw// new Error(\'Unknown Prefix '
      }
    }
  });

  grunt.registerTask('i18n-dump', 'Dump i18n file for widgets', function(){
    var output = '# Gettext Message File for Plone mockup\n' +
                 'msgid ""\n' +
                 'msgstr ""\n' +
                 '"Project-Id-Version: mockup\\n"\n' +
                 '"Last-Translator: Plone i18n <plone-i18n@lists.sourceforge.net>\\n"\n' +
                 '"Language-Team: Plone i18n <plone-i18n@lists.sourceforge.net>\\n"\n' +
                 '"MIME-Version: 1.0\\n"\n' +
                 '"Content-Type: text/plain; charset=utf-8\\n"\n' +
                 '"Content-Transfer-Encoding: 8bit\\n"\n' +
                 '"Plural-Forms: nplurals=1; plural=0;\\n"\n' +
                 '"Language-Code: en\\n"\n' +
                 '"Language-Name: English\\n"\n' +
                 '"Preferred-Encodings: utf-8\\n"\n' +
                 '"Domain: widgets\\n"\n\n';

    var okayFiles = ['xml', 'js', 'htm', 'html'];
    var found = [];
    var checkFile = function(filepath){
      var split = filepath.split('.');
      if(okayFiles.indexOf(split[split.length - 1]) === -1){
        return;
      }
      console.log('reading file: ' + filepath);
      var file = fs.readFileSync(filepath, {encoding: 'utf-8'});
      var re = /_t\((("[^"]+")|('[^']+'))(,\W{.*})?\)?\)/g;
      var m = re.exec(file);
      while (m) {
        if (m) {
          re.lastIndex = Math.max(m.index+1, re.lastIndex + 1);
          var val = m[1].replace(/['"]+/g, '');
          if(found.indexOf(val) === -1){
            output += '#: ' + filepath + '\n' +
                      'msgid "' + val + '"\n' +
                      'msgstr ""\n\n';
            found.push(val);
          }
          m = re.exec(file);
        }
      }
    };
    var checkDir = function(path){
      console.log('read folder: ' + path);
      var files = fs.readdirSync(path);
      files.forEach(function(filename){
        if(filename === 'bower_components' || filename === 'node_modules'){
          return;
        }
        var stats = fs.statSync(path + filename);
        if(stats.isDirectory()){
          checkDir(path + filename + '/');
        }else{
          checkFile(path + filename);
        }
      });
    };
    checkDir('./');
    fs.writeFileSync('../widgets.pot', output);
  });

};
