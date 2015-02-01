/**
 * Patterns store - store pattern state locally in the browser
 *
 * Copyright 2008-2012 Simplon B.V.
 * Copyright 2011 Humberto Sermeño
 * Copyright 2011 Florian Friesdorf
 */
define(function() {
    function Storage(backend, prefix) {
        this.prefix=prefix;
        this.backend=backend;
    }

    Storage.prototype._key = function Storage_key(name) {
        return this.prefix + ":" + name;
    };

    Storage.prototype._allKeys = function Storage_allKeys() {
        var keys = [],
            prefix = this.prefix + ":",
            prefix_length = prefix.length,
            key, i;

        for (i=0; i<this.backend.length; i++) {
            key=this.backend.key(i);
            if (key.slice(0, prefix_length)===prefix)
                keys.push(key);
        }
        return keys;
    };

    Storage.prototype.get = function Storage_get(name) {
        var key = this._key(name),
            value = this.backend.getItem(key);
        if (value!==null)
            value=JSON.parse(value);
        return value;
    };

    Storage.prototype.set = function Storage_set(name, value) {
        var key = this._key(name);
        return this.backend.setItem(key, JSON.stringify(value));
    };

    Storage.prototype.remove = function Storage_remove(name) {
        var key = this._key(name);
        return this.backend.removeItem(key);
    };

    Storage.prototype.clear = function Storage_clear() {
        var keys = this._allKeys();
        for (var i=0; i<keys.length; i++)
            this.backend.removeItem(keys[i]);
    };

    Storage.prototype.all = function Storage_all() {
        var keys = this._allKeys(),
            prefix_length = this.prefix.length + 1,
            lk,
            data = {};

        for (var i=0; i<keys.length; i++) {
            lk = keys[i].slice(prefix_length);
            data[lk]=JSON.parse(this.backend.getItem(keys[i]));
        }
        return data;
    };

    function ValueStorage(store, name) {
        this.store=store;
        this.name=name;
    }

    ValueStorage.prototype.get = function ValueStorage_get() {
        return this.store.get(this.name);
    }

    ValueStorage.prototype.set = function ValueStorage_get(value) {
        return this.store.set(this.name, value);
    }

    ValueStorage.prototype.remove = function ValueStorage_remove() {
        return this.store.remove(this.name);
    }

    var store = {
        supported: false,

        local: function(name) {
            return new Storage(window.localStorage, name);
        },

        session: function(name) {
            return new Storage(window.sessionStorage, name);
        },

        ValueStorage: ValueStorage,

        // Update storage options for a given element.
        updateOptions: function store_updateOptions(trigger, options) {
            if (options.store!=="none") {
                if (!trigger.id) {
                    log.warn("state persistance requested, but element has no id");
                    options.store="none";
                } else if (!store.supported) {
                    log.warn("state persistance requested, but browser does not support webstorage");
                    options.store="none";
                }
            }
            return options;
        },

    };

    // Perform the test separately since this may throw a SecurityError as
    // reported in #326
    try {
        store.supported=typeof window.sessionStorage !== 'undefined';
    } catch(e) {
    }

    return store;
});

// vim: sw=4 expandtab
