require({
    paths: {
        templates: '../templates',
        underscore: 'libs/underscore',
        text: 'libs/text',
        tpl: 'libs/tpl'
    },
    shim: {
        underscore: {
            exports: '_'
        }
    }
}, ['tpl!templates/message'], function (template) {
    'use strict';

    console.log('template = ' + template);
    document.body.innerHTML += template({message: 'Hello World!'});
});
