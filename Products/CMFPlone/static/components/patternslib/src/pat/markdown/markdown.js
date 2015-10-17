define([
    "jquery",
    "pat-logger",
    "pat-registry",
    "pat-utils",
    "pat-base",
    "pat-inject",
    "showdown",
    "showdown-github",
    "showdown-table"
], function($, logger, registry, utils, Base, inject, Showdown) {
    var log = logger.getLogger("pat.markdown");
    var is_markdown_resource = /\.md$/;

    var Markdown = Base.extend({
        name: "markdown",
        trigger: ".pat-markdown",

        init: function($el, options) {
            if (this.$el.is(this.trigger)) {
                /* This pattern can either be used standalone or as an enhancement
                * to pat-inject. The following only applies to standalone, when
                * $el is explicitly configured with the pat-markdown trigger.
                */
                var source = this.$el.is(":input") ? this.$el.val() : this.$el.text();
                this.render(source).replaceAll(this.$el);
            }
        },

        render: function(text) {
            var $rendering = $("<div/>"),
                converter = new Showdown.converter({extensions: ['table', 'prettify', 'github']});
            $rendering.html(converter.makeHtml(text));
            return $rendering;
        },

        renderForInjection: function(cfg, data) {
            var header, source = data;
            if (cfg.source && (header=/^#+\s*(.*)/.exec(cfg.source))!==null) {
                source = this.extractSection(source, header[1]);
                if (source===null) {
                    log.warn("Could not find section \"" + cfg.source + "\" in " + cfg.url);
                    return $("<div/>").attr("data-src", cfg.url);
                }
                source+="\n";  // Needed for some markdown syntax
            }
            return this.render(source).attr("data-src", cfg.source ? cfg.url+cfg.source : cfg.url);
        },

        extractSection: function(text, header) {
            var pattern, level;
            header = utils.escapeRegExp(header);
            var matcher = new RegExp(
                        "^((#+)\\s*@TEXT@\\s*|@TEXT@\\s*\\n([=-])+\\s*)$".replace(/@TEXT@/g, header), "m"),
                match = matcher.exec(text);
            if (match===null) {
                return null;
            } else if (match[2]) {
                // We have a ##-style header.
                level = match[2].length;
                pattern="^#{@LEVEL@}\\s*@TEXT@\\s*$\\n+((?:.|\\n)*?(?=^#{1,@LEVEL@}\\s)|.*(?:.|\\n)*)";
                pattern=pattern.replace(/@LEVEL@/g, level);
            } else if (match[3]) {
                // We have an underscore-style header.
                if (match[3]==="=")
                    pattern="^@TEXT@\\s*\\n=+\\s*\\n+((?:.|\\n)*?(?=^.*?\\n=+\\s*$)|(?:.|\\n)*)";
                else
                    pattern="^@TEXT@\\s*\\n-+\\s*\\n+((?:.|\\n)*?(?=^.*?\\n[-=]+\\s*$)|(?:.|\\n)*)";
            } else {
                log.error("Unexpected section match result", match);
                return null;
            }
            pattern = pattern.replace(/@TEXT@/g, header);
            matcher = new RegExp(pattern, "m");
            match = matcher.exec(text);
            if (match===null) {
                log.error("Failed to find section with known present header?");
            }
            return (match!==null) ? match[0] : null;
        }
    });

    // Add support for syntax highlighting via pat-syntax-highlight
    Showdown.extensions.prettify = function(converter) {
        return [{ type: 'output', filter: function(source){
            return source.replace(/(<pre>)?<code>/gi, function(match, pre) {
                if (pre) {
                    return '<pre class="pat-syntax-highlight" tabIndex="0"><code data-inner="1">';
                } else {
                    return '<code class="pat-syntax-highlight">';
                }
            });
        }}];
    };

    $(document).ready(function () {
        $(document.body).on("patterns-inject-triggered.pat-markdown", "a.pat-inject", function identifyMarkdownURLs() {
            /* Identify injected URLs which point to markdown files and set their
            * datatype so that we can register a type handler for them.
            */
            var cfgs = $(this).data("pat-inject");
            cfgs.forEach(function(cfg) {
                if (is_markdown_resource.test(cfg.url)) {
                    cfg.dataType = "markdown";
                }
            });
        });
    });

    inject.registerTypeHandler("markdown", {
        sources: function(cfgs, data) {
            return cfgs.map(function(cfg) {
                var pat = Markdown.init(cfg.$target);
                return pat.renderForInjection(cfg, data);
            });
        }
    });
    return Markdown;
});
