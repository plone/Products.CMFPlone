var config = module.exports;

var fs = require('fs');

var sources = JSON.parse(fs.readFileSync('bowerbuster.json', 'utf8'));
sources.push('src/**/*.js');

config.core = {
    rootPath: ".",
    environment: "browser",
    libs: [
        'components/requirejs/require.js',
        'config.js'
    ],
    sources: sources,
    tests: [
        "test/**/*.js"
    ],
    extensions: [require('buster-amd')],
    "buster-amd": {
        pathMapper: function(path) {
            return path.replace(/\.js$/, "").replace(/^\//, "../");
        }
    }
};
