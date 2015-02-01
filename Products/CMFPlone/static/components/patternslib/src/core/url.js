/**
 * Patterns URL - URL parsing utilities
 *
 * Copyright 2013 Simplon B.V.
 */
define(function() {
    function UrlArgumentParser() {
        this._cache=null;
        if (window.addEventListener)
            window.addEventListener("popstate", this._reset);
    }

    UrlArgumentParser.prototype = {
        space_pattern: /\+/g,
        keyvalue_pattern: /^(.+?)(?:=(.*))/,

        _reset: function UrlArgumentParser_reset() {
            this._cache=null;
        },

        _decodeQS: function UrlArgumentParser_decodeQS(bit) {
            return decodeURIComponent(bit.replace(this.space_pattern, " "));
        },

        _parse: function UrlArgumentParser_parse(qs) {
            var query = /\?(.+)/.exec(qs),
                params = {};

            if (query===null)
                return params;

            var parameters = query[1].split("&"),
                i, parts, key, value;
                
            for (i=0; i<parameters.length; i++) {
                if ((parts=this.keyvalue_pattern.exec(parameters[i]))===null) {
                    key=this._decodeQS(parameters[i]);
                    value=null;
                } else {
                    key=this._decodeQS(parts[1]);
                    value=this._decodeQS(parts[2]);
                }

                if (params[key]===undefined)
                    params[key]=[];
                params[key].push(value);
            }

            return params;
        },

        get: function UrlArgumentParser_get() {
            if (this._cache===null)
                this._cache=this._parse(window.location.search);
            return this._cache;
        }
    };

    var url_parser = new UrlArgumentParser();

    return {
        UrlArgumentParser: UrlArgumentParser,
        parameters: url_parser.get.bind(url_parser)
    };
});
