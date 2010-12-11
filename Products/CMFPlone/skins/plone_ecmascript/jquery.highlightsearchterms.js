/*
  Provides $.fn.highlightSearchTerms

  applies it to $('#region-content,#content') on page load,
  but ignore referrals from our own domain
*/

/*jslint nomen:false */


(function($) {
    var Highlighter,
        makeSearchKey,
        makeAddress,
        defaults;

    Highlighter = function (options) {
        $.extend(this, options);
        this.terms = this.cleanTerms(this.terms.length ? this.terms : this.getSearchTerms());
    };
    Highlighter.prototype = {
        highlight: function(startnode) {
            // Starting at startnode, highlight the terms in the tree
            if (!this.terms.length || !startnode.length) {return;}

            var self = this;
            $.each(this.terms, function(i, term) {
                startnode.find('*:not(textarea)').andSelf().contents().each(function() {
                    if (this.nodeType === 3) {
                        self.highlightTermInNode(this, term);
                    }
                });
            });
        },

        highlightTermInNode: function(node, word) {
            // wrap every occurance of word within node in a span with
            // options className.
            // word is a String, node a DOM TextNode
            var c = node.nodeValue,
                self = this,
                highlight,
                ci,
                index,
                next;

            if ($(node).parent().hasClass(self.highlightClass)) {return;}

            // Internet Explorer cannot create simple <span> tags without content
            // otherwise it'd be $('<span>').addClass(...).text(content)
            highlight = function(content) {
                return $('<span class="' + self.highlightClass + '">' +
                    content + '</span>');
            };

            ci = self.caseInsensitive;
            while (c && (index = (ci ? c.toLowerCase() : c).indexOf(word)) > -1) {
                // replace the node with [before]<span>word</span>[after]
                $(node)
                    .before(document.createTextNode(c.substr(0, index)))
                    .before(highlight(c.substr(index, word.length)))
                    .before(document.createTextNode(c.substr(index+word.length)));
                next = node.previousSibling; // text after the span
                $(node).remove();
                // wash, rinse and repeat
                node = next; c = node.nodeValue;
            }
        },

        queryStringValue: function(uri, regexp) {
            // Return the decoded value of the key=value pair in the query string
            // uri is the full URI including qs, regexp is a /key=(.*)/ pattern
            var match, pair;

            if (uri.indexOf('?') < 0) {return '';}
            uri = uri.substr(uri.indexOf('?') + 1);
            while (uri.indexOf('=') >= 0) {
                uri = uri.replace(/^\&*/, '');
                pair = uri.split('&', 1)[0];
                uri = uri.substr(pair.length);
                match = pair.match(regexp);
                if (match) {
                    return decodeURIComponent(
                        match[match.length-1].replace(/\+/g, ' '));
                }
            }
            return '';
        },

        termsFromReferrer: function() {
            // Find search terms from the referrer, if a recognized search engine
            var ref, i, se;

            ref = $.fn.highlightSearchTerms._test_referrer !== null ?
                $.fn.highlightSearchTerms._test_referrer :
                document.referrer;
            if (!ref) {return '';}

            for (i = 0; i < this.referrers.length; i+=1) {
                se = this.referrers[i];
                if (ref.match(se.address)) {return this.queryStringValue(ref, se.key);}
            }
            return '';
        },

        cleanTerms: function(terms) {
            var self = this;
            return $.unique($.map(terms, function(term) {
                term = $.trim(self.caseInsensitive ? term.toLowerCase() : term);
                return (!term || self.filterTerms.test(term)) ? null : term;
            }));
        },

        getSearchTerms: function() {
            var terms = [],
                uri = $.fn.highlightSearchTerms._test_location !== null ?
                $.fn.highlightSearchTerms._test_location :
                location.href;
            if (this.useReferrer) {
                $.merge(terms, this.termsFromReferrer().split(/\s+/));
            }
            if (this.useLocation) {
                $.merge(terms, this.queryStringValue(uri, this.searchKey).split(/\s+/));
            }
            return terms;
        }
    };

    makeSearchKey = function(key) {
        return (typeof key === 'string') ? new RegExp('^' + key + '=(.*)$', 'i') : key;
    };
    makeAddress = function(addr) {
        return (typeof addr === 'string') ? new RegExp('^https?://(www\\.)?' + addr, 'i') : addr;
    };

    $.fn.highlightSearchTerms = function(options) {
        // Wrap terms in a span with class highlightedSearchTerm.
        // See defaults for options
        options = $.extend({}, defaults, options);
        options = $.extend(options, {
            searchKey: makeSearchKey(options.searchKey),
            referrers: $.map(options.referrers, function(se) {
                return {
                    address: makeAddress(se.address),
                    key: makeSearchKey(se.key)
                };
            })
        });
        if (options.includeOwnDomain) {
            var hostname = $.fn.highlightSearchTerms._test_location !== null ?
                $.fn.highlightSearchTerms._test_location : location.hostname;
            options.referrers.push({
                address: makeAddress(hostname.replace(/\./g, '\\.')),
                key: options.searchKey
            });
        }
        new Highlighter(options).highlight(this);

        return this;
    };

    // defaults referrers is public for easy copying (for extending the
    // list) or even inplace alteration if you are so inclined.
    $.fn.highlightSearchTerms.referrers = [ // List based on http://fucoder.com/code/se-hilite/
        { address: 'google\\.',         key: 'q' },         // Google
        { address: 'search\\.yahoo\\.', key: 'p' },         // Yahoo
        { address: 'search\\.msn\\.',   key: 'q' },         // MSN
        { address: 'search\\.live\\.',  key: 'query' },     // MSN
        { address: 'search\\.aol\\.',   key: 'userQuery' }, // AOL
        { address: 'ask\\.com',         key: 'q' },         // AOL
        { address: 'altavista\\.',      key: 'q' },         // AltaVista
        { address: 'feedster\\.',       key: 'q' }          // Feedster
    ];

    defaults = {
        // array of terms to highlight; if empty we'll look up terms from the
        // location and referrer
        terms: [],

        // Use the current location query string? If so, use searchKey to find
        // what query parameter to use; it's either a string or a regexp, the
        // former will be turned into a regexp matching /^[searchKey]=(.*)$/i.
        // Note that the last group in a match *must* contain the terms.
        useLocation: true,
        searchKey: '(searchterm|SearchableText)',

        // Use the referrer to detect search engine queries? If so, use
        // referrers to detect these and their search keys. Is an
        // array of {address, key} entries; key is treated as searchKey
        // above, with address turned into '^https?://(www\.)?[address]'
        // regular expressions, if not already a regexp.
        useReferrer: true,
        referrers: $.fn.highlightSearchTerms.referrers,

        // Should the current domain name and searchKey be included in
        // the referrers?
        includeOwnDomain: true,

        // Are terms matched case insensitive?
        caseInsensitive: true,
        // what terms are never to be highlighted (regexp)?
        filterTerms: /(not|and|or)/i,
        // What class is used to mark highlighted search terms?
        highlightClass: 'highlightedSearchTerm'
    };

    // Internal use only, test framework hooks.
    $.fn.highlightSearchTerms._test_location = null;
    $.fn.highlightSearchTerms._test_referrer = null;
    $.fn.highlightSearchTerms._highlighter = Highlighter;
}(jQuery));

jQuery(function($) {
    // Highlight search results, but ignore referrals from our own domain
    // when displaying search results.
    $('#region-content,#content').highlightSearchTerms({
        includeOwnDomain: $('dl.searchResults').length === 0
    });
});
