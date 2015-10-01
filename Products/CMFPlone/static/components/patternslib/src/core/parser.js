/**
 * Patterns parser - Argument parser
 *
 * Copyright 2012-2013 Florian Friesdorf
 * Copyright 2012-2013 Simplon B.V. - Wichert Akkerman
 */
define([
    "jquery",
    "underscore",
    "pat-logger"
], function($, _, logger) {
    "use strict";

    function ArgumentParser(name, opts) {
        opts = opts || {};
        this.order = [];
        this.parameters = {};
        this.attribute = "data-pat-" + name;
        this.enum_values = {};
        this.enum_conflicts = [];
        this.groups = {};
        this.possible_groups = {};
        this.log = logger.getLogger(name + ".parser");
    }

    ArgumentParser.prototype = {
        group_pattern: /([a-z][a-z0-9]*)-([A-Z][a-z0-0\-]*)/i,
        json_param_pattern: /^\s*{/i,
        named_param_pattern: /^\s*([a-z][a-z0-9\-]*)\s*:(.*)/i,
        token_pattern: /((["']).*?(?!\\)\2)|\s*(\S+)\s*/g,

        _camelCase: function(str) {
            return str.replace(/\-([a-z])/g, function(_, p1){
                return p1.toUpperCase();
            });
        },

        addAlias: function argParserAddAlias(alias, original) {
            /* Add an alias for a previously added parser argument.
             *
             * Useful when you want to support both US and UK english argument
             * names.
             */
            if (this.parameters[original]) {
                this.parameters[original].alias = alias;
            } else {
                throw("Attempted to add an alias \""+alias+"\" for a non-existing parser argument \""+original+"\".");
            }
        },

        addGroupToSpec: function argParserAddGroupToSpec(spec) {
            /* Determine wether an argument being parsed can be grouped and
             * update its specifications object accordingly.
             *
             * Internal method used by addArgument and addJSONArgument
             */
            var m = spec.name.match(this.group_pattern);
            if (m) {
                var group = m[1],
                    field = m[2];
                if (group in this.possible_groups) {
                    var first_spec = this.possible_groups[group],
                        first_name = first_spec.name.match(this.group_pattern)[2];
                    first_spec.group = group;
                    first_spec.dest = first_name;
                    this.groups[group] = new ArgumentParser();
                    this.groups[group].addArgument(
                            first_name, first_spec.value, first_spec.choices, first_spec.multiple);
                    delete this.possible_groups[group];
                }
                if (group in this.groups) {
                    this.groups[group].addArgument(field, spec.value, spec.choices, spec.multiple);
                    spec.group = group;
                    spec.dest = field;
                } else {
                    this.possible_groups[group] = spec;
                    spec.dest = this._camelCase(spec.name);
                }
            }
            return spec;
        },

        addJSONArgument: function argParserAddJSONArgument(name, default_value) {
            /* Add an argument where the value is provided in JSON format.
             *
             * This is a different usecase than specifying all arguments to
             * the data-pat-... attributes in JSON format, and instead is part
             * of the normal notation except that a value is in JSON instead of
             * for example a string.
             */
            this.order.push(name);
            this.parameters[name] = this.addGroupToSpec({
                name: name,
                value: default_value,
                dest: name,
                group: null,
                type: "json"
            });
        },

        addArgument: function ArgParserAddArgument(name, default_value, choices, multiple) {
            var spec = {
                name: name,
                value: (multiple && !Array.isArray(default_value)) ? [default_value] : default_value,
                multiple: multiple,
                dest: name,
                group: null
            };
            if (choices && Array.isArray(choices) && choices.length) {
                spec.choices = choices;
                spec.type = this._typeof(choices[0]);
                for (var i=0; i<choices.length; i++) {
                    if (this.enum_conflicts.indexOf(choices[i])!==-1) {
                        continue;
                    } else if (choices[i] in this.enum_values) {
                        this.enum_conflicts.push(choices[i]);
                        delete this.enum_values[choices[i]];
                    } else {
                        this.enum_values[choices[i]]=name;
                    }
                }
            } else if (typeof spec.value==="string" && spec.value.slice(0, 1)==="$") {
                spec.type = this.parameters[spec.value.slice(1)].type;
            } else {
                // Note that this will get reset by _defaults if default_value is a function.
                spec.type = this._typeof(multiple ? spec.value[0] : spec.value);
            }
            this.order.push(name);
            this.parameters[name] = this.addGroupToSpec(spec);
        },

        _typeof: function argParserTypeof(obj) {
            var type = typeof obj;
            if (obj===null)
                return "null";
            return type;
        },

        _coerce: function argParserCoerce(name, value) {
            var spec = this.parameters[name];
            if (typeof value !== spec.type)
                try {
                    switch (spec.type) {
                        case "json":
                            value = JSON.parse(value);
                            break;
                        case "boolean":
                            if (typeof value === "string") {
                                value = value.toLowerCase();
                                var num = parseInt(value, 10);
                                if (!isNaN(num))
                                    value = !!num;
                                else
                                    value=(value==="true" || value==="y" || value==="yes" || value==="y");
                            } else if (typeof value === "number")
                                value = !!value;
                            else
                                throw ("Cannot convert value for " + name + " to boolean");
                            break;
                        case "number":
                            if (typeof value === "string") {
                                value = parseInt(value, 10);
                                if (isNaN(value))
                                    throw ("Cannot convert value for " + name + " to number");
                            } else if (typeof value === "boolean")
                                value = value + 0;
                            else
                                throw ("Cannot convert value for " + name + " to number");
                            break;
                        case "string":
                            value=value.toString();
                            break;
                        case "null":  // Missing default values
                        case "undefined":
                            break;
                        default:
                            throw ("Do not know how to convert value for " + name + " to " + spec.type);
                    }
                } catch (e) {
                    this.log.warn(e);
                    return null;
                }

            if (spec.choices && spec.choices.indexOf(value)===-1) {
                this.log.warn("Illegal value for " + name + ": " + value);
                return null;
            }
            return value;
        },

        _set: function argParserSet(opts, name, value) {
            if (!(name in this.parameters)) {
                this.log.debug("Ignoring value for unknown argument " + name);
                return;
            }
            var spec = this.parameters[name],
                parts, i, v;
            if (spec.multiple) {
                if (typeof value === "string") {
                    parts = value.split(/,+/);
                } else {
                    parts = value;
                }
                value = [];
                for (i=0; i<parts.length; i++) {
                    v = this._coerce(name, parts[i].trim());
                    if (v!==null)
                        value.push(v);
                }
            } else {
                value = this._coerce(name, value);
                if (value===null)
                    return;
            }
            opts[name] = value;
        },

        _split: function argParserSplit(text) {
            var tokens = [];
            text.replace(this.token_pattern, function(match, quoted, _, simple) {
                if (quoted)
                    tokens.push(quoted);
                else if (simple)
                    tokens.push(simple);
            });
            return tokens;
        },

        _parseExtendedNotation: function argParserParseExtendedNotation(argstring) {
            var opts = {};
            var parts = argstring.replace(";;", "\xff").split(";")
                        .map(function(el) { return el.replace("\xff", ";"); });
            _.each(parts, function (part, i) {
                if (!part) { return; }
                var matches = part.match(this.named_param_pattern);
                if (!matches) {
                    this.log.warn("Invalid parameter: " + part);
                    return;
                }
                var name = matches[1],
                    value = matches[2].trim(),
                    arg = _.chain(this.parameters).where({'alias': name}).value(),
                    is_alias = arg.length === 1;

                if (is_alias) {
                    this._set(opts, arg[0].name, value);
                } else if (name in this.parameters) {
                    this._set(opts, name, value);
                } else if (name in this.groups) {
                    var subopt = this.groups[name]._parseShorthandNotation(value);
                    for (var field in subopt) {
                        this._set(opts, name+"-"+field, subopt[field]);
                    }
                } else {
                    this.log.warn("Unknown named parameter " + matches[1]);
                    return;
                }
            }.bind(this));
            return opts;
        },

        _parseShorthandNotation: function argParserParseShorthandNotation(parameter) {
            var parts = this._split(parameter),
                opts = {},
                positional = true,
                i, part, flag, sense;

            i=0;
            while (parts.length) {
                part=parts.shift().trim();
                if (part.slice(0, 3)==="no-") {
                    sense=false;
                    flag=part.slice(3);
                } else {
                    sense=true;
                    flag=part;
                }
                if (flag in this.parameters && this.parameters[flag].type==="boolean") {
                    positional=false;
                    this._set(opts, flag, sense);
                } else if (flag in this.enum_values) {
                    positional=false;
                    this._set(opts, this.enum_values[flag], flag);
                } else if (positional)
                    this._set(opts, this.order[i], part);
                else {
                    parts.unshift(part);
                    break;
                }
                i++;
                if (i>=this.order.length)
                    break;
            }
            if (parts.length)
                this.log.warn("Ignore extra arguments: " + parts.join(" "));
            return opts;
        },

        _parse: function argParser_parse(parameter) {
            var opts, extended, sep;
            if (!parameter) { return {}; }
            if (parameter.match(this.json_param_pattern)) {
                try {
                    return JSON.parse(parameter);
                } catch (e) {
                    this.log.warn("Invalid JSON argument found: "+parameter);
                }
            }
            if (parameter.match(this.named_param_pattern)) {
                return this._parseExtendedNotation(parameter);
            }
            sep = parameter.indexOf(";");
            if (sep===-1) {
                return this._parseShorthandNotation(parameter);
            }
            opts = this._parseShorthandNotation(parameter.slice(0, sep));
            extended = this._parseExtendedNotation(parameter.slice(sep+1));
            for (var name in extended)
                opts[name] = extended[name];
            return opts;
        },

        _defaults: function argParserDefaults($el) {
            var result = {};
            for (var name in this.parameters)
                if (typeof this.parameters[name].value==="function")
                    try {
                        result[name]=this.parameters[name].value($el, name);
                        this.parameters[name].type=typeof result[name];
                    } catch(e) {
                        this.log.error("Default function for " + name + " failed.");
                    }
                else
                    result[name]=this.parameters[name].value;
            return result;
        },

        _cleanupOptions: function argParserCleanupOptions(options) {
            var keys = Object.keys(options),
                i, spec, name, target;

            // Resolve references
            for (i=0; i<keys.length; i++) {
                name=keys[i];
                spec=this.parameters[name];
                if (spec===undefined)
                    continue;

                if (options[name]===spec.value &&
                        typeof spec.value==="string" && spec.value.slice(0, 1)==="$")
                    options[name]=options[spec.value.slice(1)];
            }

            // Move options into groups and do renames
            keys=Object.keys(options);
            for (i=0; i<keys.length; i++) {
                name=keys[i];
                spec=this.parameters[name];
                if (spec===undefined)
                    continue;

                if (spec.group)  {
                    if (typeof options[spec.group]!=="object")
                        options[spec.group]={};
                    target=options[spec.group];
                } else
                    target=options;

                if (spec.dest!==name) {
                    target[spec.dest]=options[name];
                    delete options[name];
                }
            }
        },

        parse: function argParserParse($el, options, multiple, inherit) {
            if (typeof options==="boolean" && multiple===undefined) {
                multiple=options;
                options={};
            }
            inherit = (inherit!==false);
            var stack = inherit ? [[this._defaults($el)]] : [[{}]];
            var $possible_config_providers = inherit ? $el.parents().andSelf() : $el,
                final_length = 1,
                i, data, frame;
            for (i=0; i<$possible_config_providers.length; i++) {
                data = $possible_config_providers.eq(i).attr(this.attribute);
                if (data) {
                    var _parse = this._parse.bind(this); // Needed to fix binding in map call
                    if (data.match(/&&/))
                        frame=data.split(/\s*&&\s*/).map(_parse);
                    else
                        frame=[_parse(data)];
                    final_length = Math.max(frame.length, final_length);
                    stack.push(frame);
                }
            }
            if (typeof options==="object") {
                if (Array.isArray(options)) {
                    stack.push(options);
                    final_length=Math.max(options.length, final_length);
                } else
                    stack.push([options]);
            }

            if (!multiple) {
                final_length=1;
            }
            var results=[], frame_length, x, xf;
            for (i=0; i<final_length; i++)
                results.push({});

            for (i=0; i<stack.length; i++) {
                frame=stack[i];
                frame_length=frame.length-1;

                for (x=0; x<final_length; x++) {
                    xf=(x>frame_length) ? frame_length : x;
                    results[x]=$.extend(results[x], frame[xf]);
                }
            }
            for (i=0; i<results.length; i++)
                this._cleanupOptions(results[i]);

            return multiple ? results : results[0];
        }
    };
    // BBB
    ArgumentParser.prototype.add_argument = ArgumentParser.prototype.addArgument;
    return ArgumentParser;
});
// jshint indent: 4, browser: true, jquery: true, quotmark: double
// vim: sw=4 expandtab
