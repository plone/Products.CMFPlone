/**
 * Patterns pat-polyfill-colour - Polyfill for colour inputs.
 *
 * Copyright 2014 Marko Durkovic
 * Copyright 2014 Simplon B.V. - Wichert Akkerman
 */
define([
    "pat-registry",
    "spectrum"
], function(registry) {
    var _ = {
        name: "polyfill-color",
        trigger: "input.pat-colour-picker,input.pat-color-picker",
        init: function($el) {
            return $el.spectrum({preferredFormat: "hex"});
        }
    };

    registry.register(_);
    return _;
});

// vim: sw=4 expandtab
