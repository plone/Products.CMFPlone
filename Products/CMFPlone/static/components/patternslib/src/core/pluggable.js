define([
    "jquery",
    "pat-utils"
], function($, utils) {
    var pluggable = {

        extend: function (attrs) {
            return utils.extend(this, attrs);
        },

        registerPlugin: function (name, callback) {
            this.plugins[name] = callback;
        },

        initializePlugins: function () {
            var i, keys = _.keys(this.plugins);
            var args = arguments;
            for (i=0; i<keys.length; i++) {
                $.proxy(this.plugins[keys[i]], this).apply(this, args);
            }
            return args;
        }
    };
    return pluggable;
});
