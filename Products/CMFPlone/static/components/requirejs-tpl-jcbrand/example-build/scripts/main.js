
define('text',{});
define('underscore',{});
define('tpl',{load: function(id){throw new Error("Dynamic load not allowed: " + id);}});
define('tpl!templates/message',[], function () { return function(obj){
var __t,__p='',__j=Array.prototype.join,print=function(){__p+=__j.call(arguments,'');};
with(obj||{}){
__p+='<h1>\n    Message\n</h1>\n<p>\n    '+
((__t=( message ))==null?'':__t)+
'\n</p>';
}
return __p;
}; });

require({
    paths: {
        templates: '../templates',
        underscore: 'libs/underscore',
        text: 'libs/text',
        tpl: 'libs/tpl'
    },
    shim: {
        'underscore': {
            exports: '_'
        }
    }
}, ['tpl!templates/message'], function (template) {
    

    console.log('template = ' + template);
    document.body.innerHTML += template({message: 'Hello World!'});
});

define("main", function(){});
