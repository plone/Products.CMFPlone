define([
  'sinon',
  'jquery',
  'underscore'
], function(sinon, $, _) {
  'use strict';

  function getQueryVariable(url, variable) {
    var query;
    if(url.indexOf('?') !== -1){
      query = url.split('?')[1];
      if (query === undefined) {
        return null;
      }
    }else{
      query = url;
    }
    var vars = query.split('&');
    for (var i = 0; i < vars.length; i += 1) {
      var pair = vars[i].split('=');
      if (decodeURIComponent(pair[0]) === variable) {
        return decodeURIComponent(pair[1]);
      }
    }
    return null;
  }

  var server = sinon.fakeServer.create();
  server.xhr.useFilters = true;
  var okayUrls = [
  ];
  server.xhr.addFilter(function(method, url) {
    //whenever the this returns true the request will not faked, is this working?
    return url.indexOf('tests/json/') !== -1 ||
           url.indexOf('ace/lib') !== -1 ||
           /(?![filemanager])\..*\.xml$/i.test(url) ||
           /(?![filemanager])\..*\.js$/i.test(url);
  });
  server.autoRespond = true;
  server.autoRespondAfter = 200;

  server.respondWith('GET', /select2-test\.json/, function (xhr, id) {
    var items = [
      {id: 'red', text: 'Red'},
      {id: 'green', text: 'Green'},
      {id: 'blue', text: 'Blue'},
      {id: 'orange', text: 'Orange'},
      {id: 'yellow', text: 'Yellow'}
    ];
    xhr.respond(200, { 'Content-Type': 'application/json' }, JSON.stringify({
      total: items.length,
      results: items
    }));
  });

  server.respondWith('GET', /search\.json/, function (xhr, id) {
    var items = [
      {
        UID: '123sdfasdf',
        getURL: 'http://localhost:8081/news/aggregator',
        portal_type: 'Collection',
        Description: 'Site News',
        Title: 'News'
      },
      {
        UID: 'fooasdfasdf1123asZ',
        getURL: 'http://localhost:8081/news/aggregator',
        portal_type: 'Collection',
        Description: 'Site News',
        Title: 'Another Item'
      },
      {
        UID: 'fooasdfasdf1231as',
        getURL: 'http://localhost:8081/news/aggregator',
        portal_type: 'Collection',
        Description: 'Site News',
        Title: 'News'
      },
      {
        UID: 'fooasdfasdf12231451',
        getURL: 'http://localhost:8081/news/aggregator',
        portal_type: 'Collection',
        Description: 'Site News',
        Title: 'Another Item'
      },
      {
        UID: 'fooasdfasdf1235dsd',
        getURL: 'http://localhost:8081/news/aggregator',
        portal_type: 'Collection',
        Description: 'Site News',
        Title: 'News'
      },
      {
        UID: 'fooasdfasd345345f',
        getURL: 'http://localhost:8081/news/aggregator',
        portal_type: 'Collection',
        Description: 'Site News',
        Title: 'Another Item'
      },
      {
        UID: 'fooasdfasdf465',
        getURL: 'http://localhost:8081/news/aggregator',
        portal_type: 'Collection',
        Description: 'Site News',
        Title: 'News'
      },
      {
        UID: 'fooaewrwsdfasdf',
        getURL: 'http://localhost:8081/news/aggregator',
        portal_type: 'Collection',
        Description: 'Site News',
        Title: 'Another Item'
      },
      {
        UID: 'fooasdfasd123f',
        getURL: 'http://localhost:8081/news/aggregator',
        portal_type: 'Collection',
        Description: 'Site News',
        Title: 'News'
      },
      {
        UID: 'fooasdfasdas123f',
        getURL: 'http://localhost:8081/news/aggregator',
        portal_type: 'Collection',
        Description: 'Site News',
        Title: 'Another Item'
      },
      {
        UID: 'fooasdfasdfsdf',
        getURL: 'http://localhost:8081/news/aggregator',
        portal_type: 'Collection',
        Description: 'Site News',
        Title: 'News'
      },
      {
        UID: 'fooasdfasdf',
        getURL: 'http://localhost:8081/news/aggregator',
        portal_type: 'Collection',
        Description: 'Site News',
        Title: 'Another Item'
      }
    ];

    var results = [];
    var batch = JSON.parse(getQueryVariable(xhr.url, 'batch'));

    var query = JSON.parse(getQueryVariable(xhr.url, 'query'));

    if (query.criteria[0].v === 'none*') {
      results = [];
    } else {
      if (batch) {
        var start, end;
        start = (batch.page - 1) * batch.size;
        end = start + batch.size;
        results = items.slice(start, end);
      }
    }

    xhr.respond(200, { 'Content-Type': 'application/json' }, JSON.stringify({
      total: results.length,
      results: results
    }));
  });

  server.respondWith('GET', /livesearch\.json/, function (xhr, id) {
    var items = [{
      url: 'http://localhost:8081/news/aggregator',
      description: 'Site News',
      title: 'News',
      state: 'published'
    }, {
      url: 'http://localhost:8081/news/aggregator',
      description: 'Site News',
      title: 'News',
      state: 'published'
    }];
    xhr.respond(200, { 'Content-Type': 'application/json' }, JSON.stringify({
      total: items.length,
      items: items
    }));
  });

  // define here so it's the same for the entire page load.
  // these are all random items on the root of the site
  var randomItems = [];
  var basePaths = ['/', '/news/', '/projects/', '/about/'];
  var possibleNames = ['Document', 'News Item', 'Info', 'Blog Item'];
  var possibleTags = ['one', 'two', 'three', 'four'];

  function generateUID(size) {
    if (!size) {
      size = 30;
    }
    var text = '';
    var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

    for (var i = 0; i < size; i = i + 1) {
      text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
  }
  for (var pathi = 0; pathi < basePaths.length; pathi = pathi + 1) {
    var basePath = basePaths[pathi];
    for (var j = 0; j < 1000; j = j + 1) {
      randomItems.push({
        UID: generateUID(),
        Title: possibleNames[Math.floor(Math.random() * possibleNames.length)] + ' ' + j,
        path: basePath + generateUID(8),
        portal_type: 'Document'
      });
    }
  }

  server.respondWith(/relateditems-test\.json/, function(xhr, id) {
    var searchables = [
      {UID: 'jasdlfdlkdkjasdf', Title: 'Some Image', path: '/test.png', portal_type: 'Image'},
      {UID: 'asdlfkjasdlfkjasdf', Title: 'News', path: '/news', portal_type: 'Folder'},
      {UID: '124asdfasasdaf34', Title: 'About', path: '/about', portal_type: 'Folder'},
      {UID: 'asdf1234', Title: 'Projects', path: '/projects', portal_type: 'Folder'},
      {UID: 'asdf1234gsad', Title: 'Contact', path: '/contact', portal_type: 'Document'},
      {UID: 'asdv34sdfs', Title: 'Privacy Policy', path: '/policy', portal_type: 'Document'},
      {UID: 'asdfasdf234sdf', Title: 'Our Process', path: '/our-process', portal_type: 'Folder'},
      {UID: 'asdhsfghyt45', Title: 'Donate', path: '/donate-now', portal_type: 'Document'},
      // about
      {UID: 'gfn5634f', Title: 'About Us', path: '/about/about-us', portal_type: 'Document'},
      {UID: '45dsfgsdcd', Title: 'Philosophy', path: '/about/philosophy', portal_type: 'Document'},
      {UID: 'dfgsdfgj675', Title: 'Staff', path: '/about/staff', portal_type: 'Folder'},
      {UID: 'sdfbsfdh345', Title: 'Board of Directors', path: '/about/board-of-directors', portal_type: 'Document'},
      // staff
      {UID: 'asdfasdf9sdf', Title: 'Mike', path: '/about/staff/mike', portal_type: 'Document'},
      {UID: 'cvbcvb82345', Title: 'Joe', path: '/about/staff/joe', portal_type: 'Document'}
    ];
    searchables = searchables.concat(randomItems);

    var addSomeData = function(list) {
      /* add getURL value, review_state, modification, creation */
      var dates = [
        'January 1, 2011',
        'February 10, 2012',
        'March 12, 2013',
        'April 1, 2012',
        'May 20, 2013'
      ];
      for (var i = 0; i < list.length; i = i + 1) {
        var data = list[i];
        data.getURL = window.location.origin + data.path;
        data['review_state'] = ['published', 'private', 'review'][Math.floor(Math.random() * 3)];  // jshint ignore:line
        data.CreationDate = dates[Math.floor(Math.random() * dates.length)];
        data.ModificationDate = dates[Math.floor(Math.random() * dates.length)];
        data.EffectiveDate = dates[Math.floor(Math.random() * dates.length)];
        data.Subject = [
          possibleTags[Math.floor(Math.random() * possibleTags.length)],
          possibleTags[Math.floor(Math.random() * possibleTags.length)]
        ];
        data.id = data.Title.replace(' ', '-').toLowerCase();
        if (data.portal_type === 'Folder') {
          data['is_folderish'] = true;  // jshint ignore:line
        } else {
          data['is_folderish'] = false;  // jshint ignore:line
        }
      }
    };
    addSomeData(searchables);
    searchables[0].getURL = window.location.origin + '/tests/images/plone.png';
    searchables[0].path = '/tests/images/plone.png';

    var results = [];
    // grab the page number and number of items per page -- note, page is 1-based from Select2
    var batch = getQueryVariable(xhr.url, 'batch');
    var page = 1;
    var pageSize = 10;
    if (batch) {
      batch = $.parseJSON(batch);
      page = batch.page;
      pageSize = batch.size;
    }
    page = page - 1;

    var query = getQueryVariable(xhr.url, 'query');
    var path = null;
    var term = '';
    if (query) {
      query = $.parseJSON(query);
      for (var i = 0; i < query.criteria.length; i = i + 1) {
        var criteria = query.criteria[i];
        if (criteria.i === 'path') {
          path = criteria.v.split('::')[0];
        } else {
          term = criteria.v;
        }
      }
    }

    // this seach is for basically searching the entire hierarchy -- this IS NOT the browse "search"
    function search(items, term) {
      results = [];
      if (term === undefined) {
        return searchables;
      }
      _.each(items, function(item) {
        var q;
        var keys = (item.UID + ' ' + item.Title + ' ' + item.path + ' ' + item.portal_type).toLowerCase();
        if (typeof(term) === 'object') {
          for (var i = 0; i < term.length; i = i + 1) {
            q = term[i].toLowerCase();
            if (keys.indexOf(q) > -1) {
              results.push(item);
              break;
            }
          }
        } else {
          q = term.toLowerCase().replace('*', '');
          if (keys.indexOf(q) > -1) {
            results.push(item);
          }
        }
      });
    }

    function browse(items, q, p) {
      results = [];
      var path = p.substring(0, p.length - 1);
      var splitPath = path.split('/');
      var fromPath = [];
      _.each(items, function(item) {
        var itemSplit = item.path.split('/');
        if (item.path.indexOf(path) === 0 && itemSplit.length - 1 === splitPath.length) {
          fromPath.push(item);
        }
      });
      if (q === undefined) {
        return fromPath;
      }
      search(fromPath, q);
    }
    if (path) {
      browse(searchables, term, path);
    } else {
      search(searchables, term);
    }

    xhr.respond(200, { 'Content-Type': 'application/json' },
      JSON.stringify({
        total: results.length,
        results: results.slice(page * pageSize, (page * pageSize) + (pageSize - 1))
      })
    );
  });

  server.respondWith('GET', /something\.html/, [
    200,
    { 'Content-Type': 'text/html' },
    '<html> ' +
    '<head></head>' +
    '<body> ' +
    '<div id="content">' +
    '<h1>Content from AJAX</h1>' +
    '<p>Ah, it is a rock, though. Should beat everything.</p>' +
    '</body> ' +
    '</html>'
  ]);

  server.respondWith('GET', /something-link\.html/, [
    200,
    { 'Content-Type': 'text/html' },
    '<html> ' +
    '<head></head>' +
    '<body> ' +
    '<div id="content">' +
    '<h1>Content from AJAX with a link</h1>' +
    '<p>Ah, it is a rock, though. Should beat <a href="something-else.html">link</a> everything.</p>' +
    '</body> ' +
    '</html>'
  ]);

  server.respondWith('GET', /something-else\.html/, [
    200,
    { 'Content-Type': 'text/html' },
    '<html> ' +
    '<head></head>' +
    '<body> ' +
    '<div id="content">' +
    '<h1>Something else</h1>' +
    '<p>We loaded a link.</p>' +
    '</body> ' +
    '</html>'
  ]);

  server.respondWith('GET', /modal-form\.html/, [
    200,
    { 'Content-Type': 'text/html' },
    '<html> ' +
    '<head></head>' +
    '<body> ' +
    '<div id="content">' +
    '<h1>Modal with Form</h1>' +
    '<p>This modal contains a form.</p>' +
    '<form method="POST" action="/modal-submit.html">' +
    '  <label for="name">Name:</label><input type="text" name="name" />' +
    '  <div class="formControls"> ' +
    '    <input type="submit" class="btn btn-primary" value="Submit" name="submit" />' +
    '  </div> ' +
    '</form>' +
    '</body> ' +
    '</html>'
  ]);

  server.respondWith('POST', /modal-submit\.html/, function(xhr, id) {
    var name = getQueryVariable('?' + xhr.requestBody, 'name');
    xhr.respond(200, {'content-Type': 'text/html'},
      '<html> ' +
      '  <head></head>' +
      '  <body> ' +
      '    <div id="content">' +
      '      <h1>Hello, ' + _.escape(name) + '</h1>' +
      '      <p>Thanks!</p>' +
      '  </body> ' +
      '</html>'
    );
  });

  server.respondWith('POST', /upload/, function(xhr, id) {
    xhr.respond(200, {'content-Type': 'application/json'},
      JSON.stringify({
        url: 'http://localhost:8000/blah.png',
        uid: 'sldlfkjsldkjlskdjf',
        name: 'blah.png',
        filename: 'blah.png',
        portal_type: 'Image',
        size: 239292
      })
    );
  });

  server.respondWith('GET', /portal_factory\/@@querybuilder_html_results/, function(xhr, id) {
    var content = $('#querystring-example-results').text();
    xhr.respond(200, {'content-Type': 'text/html'}, content);
  });
  server.respondWith('GET', /portal_factory\/@@querybuildernumberofresults/, function(xhr, id) {
    var content = $('#querystring-number-results-example-results').text();
    xhr.respond(200, {'content-Type': 'text/html'}, content);
  });

  var basicActions = [
    '/moveitem',
    '/copy',
    '/cut',
    '/delete',
    '/workflow',
    '/tags',
    '/properties',
    '/paste',
    '/order',
    '/rename',
    '/rearrange'
  ];

  var actionData = {
    '/copy': function(xhr) {
      var selection = JSON.parse(getQueryVariable('?' + xhr.requestBody, 'selection'));
      return {
        status: 'success',
        msg: selection.length + ' items copied'
      };
    },
    '/cut': function(xhr) {
      var selection = JSON.parse(getQueryVariable('?' + xhr.requestBody, 'selection'));
      return {
        status: 'success',
        msg: selection.length + ' items cut'
      };
    },
    '/paste': function(xhr) {
      var selection = JSON.parse(getQueryVariable('?' + xhr.requestBody, 'selection'));
      return {
        status: 'success',
        msg: 'pasted ' + selection.length + ' items'
      };
    },
    '/order': function(xhr) {
      return {
        status: 'success',
        msg: 'Folder ordering set'
      };
    },
    '/tags': function(xhr) {
      var selection = JSON.parse(getQueryVariable('?' + xhr.requestBody, 'selection'));
      return {
        status: 'success',
        msg: 'Tags updated for ' + selection.length + ' items'
      };
    },
    '/properties': function(xhr) {
      var selection = JSON.parse(getQueryVariable('?' + xhr.requestBody, 'selection'));
      return {
        status: 'success',
        msg: 'Properties updated for ' + selection.length + ' items'
      };
    },
    '/rename': function(xhr) {
      var torename = JSON.parse(getQueryVariable('?' + xhr.requestBody, 'torename'));
      return {
        status: 'success',
        msg: 'Renamed ' + torename.length + ' items'
      };
    },
    '/workflow': function(xhr) {
      var selection = JSON.parse(getQueryVariable('?' + xhr.requestBody, 'selection'));
      if (xhr.requestBody.indexOf('transitions') !== -1) {
        var transitions = JSON.parse(getQueryVariable('?' + xhr.requestBody, 'transitions'));
        // get possible transitions...
        return {
          status: 'success',
          transitions: [{
            id: 'publish',
            title: 'Publish'
          }, {
            id: 'retract',
            title: 'Retract'
          }]
        };
      } else {
        return {
          status: 'success',
          msg: 'Workflow updated for ' + selection.length + ' items'
        };
      }
    },
    '/delete': function(xhr) {
      var selection = JSON.parse(getQueryVariable('?' + xhr.requestBody, 'selection'));
      return {
        status: 'success',
        msg: 'Deleted ' + selection.length + ' items'
      };
    },
    '/rearrange': function(xhr) {
      var selection = JSON.parse(getQueryVariable('?' + xhr.requestBody, 'selection'));
      return {
        status: 'success',
        msg: 'Rearranged items'
      };
    }
  };

  _.each(basicActions, function(action) {
    server.respondWith('POST', action, function(xhr, id) {
      server.autoRespondAfter = 200;
      var data = {
        status: 'success'
      };
      if (actionData[action]) {
        data = actionData[action](xhr);
      }
      xhr.respond(200, { 'Content-Type': 'application/json' }, JSON.stringify(data));
    });
  });

  server.respondWith('GET', /context-info/, function(xhr, id) {
    server.autoRespondAfter = 200;
    var data = {
      breadcrumbs: []
    };
    if (xhr.url.indexOf('http://') === -1){
      _.each(xhr.url.split('/'), function(val) {
        if (val !== '' && val !== 'context-info'){
          val = val.charAt(0).toUpperCase() + val.slice(1);
          data.breadcrumbs.push({
            title: val
          });
        }
      });
      data.object = {UID: 'asdlfkjasdlfkjasdf', Title: 'News', path: '/news', portal_type: 'Folder'};
    }
    xhr.respond(200, { 'Content-Type': 'application/json' }, JSON.stringify(data));
  });

  server.respondWith('POST', /filemanager-actions/, function(xhr, id) {
    xhr.respond(200, { 'Content-Type': 'application/json' }, JSON.stringify({}));
  });

  server.respondWith('GET', /filemanager-actions/, function(xhr, id) {
    server.autoRespondAfter = 200;
    var action = getQueryVariable(xhr.url, 'action');
    var data;

    if (action === 'dataTree'){
      data = [{
        label: 'css',
        folder: true,
        children: [{
          id: 1,
          label: 'style.css',
          folder: false
        },{
          id: 2,
          label: 'tree.css',
          folder: false
        }]
      },{
        label: 'js',
        folder: true,
        children: [{
          id: 3,
          label: 'jquery.js',
          folder: false
        },{
          id: 4,
          label: 'tree.js',
          folder: false
        }]
      },{
        id: 5,
        label: 'index.html',
        folder: false
      },{
        id: 6,
        label: 'rules.xml',
        folder: false
      }];
      xhr.respond(200, { 'Content-Type': 'application/json' }, JSON.stringify(data));
    } else if (action === 'getFile'){

      var path = getQueryVariable(xhr.url, 'path');
      var extension = path.substr( path.lastIndexOf('.') + 1 );
      data = '';

      if (extension === 'js'){
        data = 'var foo = function() { \n\talert("Hi!"); \n};';
      } else if (extension === 'css'){
        data = '#content.highlight { \n\tbackground-color: #D1F03A; \n}';
      } else if (extension === 'html'){
        data = '<html>\n\t<body>\n\t\t<p>Hi!</p>\n\t</body>\n</html>';
      } else if (extension === 'xml'){
        data = '<?xml version="1.0" encoding="UTF-8"?>\n' +
          '<rules\n' +
            'xmlns="http://namespaces.plone.org/diazo"\n' +
            'xmlns:css="http://namespaces.plone.org/diazo/css"\n' +
            'xmlns:xsl="http://www.w3.org/1999/XSL/Transform">\n\n' +
            '<theme href="theme.html" />\n' +
            '<replace css:theme="html head title" css:content="html head title" />\n' +
            '<replace css:content-children="#content" css:theme-children="#content" />\n' +
          '</rules>';
      } else {
        data = 'foobar';
      }
      xhr.respond(200, {'Content-Type': 'application/json'}, JSON.stringify({
        path: path,
        data: data
      }));
    }
  });

  server.respondWith('GET', /search-resources/, function(xhr, id) {
    server.autoRespondAfter = 200;
    xhr.respond(200, {'Content-Type': 'application/json'}, JSON.stringify([{
      id: 'plone.app.layout.viewlets.title.pt'
    }, {
      id: 'plonetheme.sunburst.resources.logo.png'
    }]));
  });

  server.respondWith('GET', /resources-registry/, function(xhr, id) {
    server.autoRespondAfter = 200;
    xhr.respond(200, {'Content-Type': 'text/plain'}, 'var foo = "bar";');
  });

  server.respondWith('POST', /registry-manager/, function(xhr, id) {
    server.autoRespondAfter = 200;
    var action = getQueryVariable(xhr.requestBody, 'action');
    var data = {};
    if(action === 'js-build-config'){
      data = {
        paths: {
          'autotoc': 'patterns/autotoc/pattern',
          'mockup-patterns-base': 'bower_components/mockup-core/js/pattern',
          'jquery': 'bower_components/jquery/dist/jquery',
          'pat-registry': 'bower_components/patternslib/src/core/registry'
        },
        include: ['autotoc']
      };
    }else if(action === 'less-build-config'){
      data = {
        'less': ['patterns/resourceregistry/pattern.resourceregistry.less']
      };
    }else if(action === 'save-js-build'){
      data = {
        'filepath': '++plone++static/autotoc.js'
      };
    }else if(action === 'save-less-build'){
      data = {
        'filepath': '++plone++static/autotoc.css'
      };
    }
    xhr.respond(200, {'Content-Type': 'application/json'}, JSON.stringify(data));
  });
  return server;

});
