/**
 * Patterns logger - wrapper around logging library
 *
 * Copyright 2012-2013 Florian Friesdorf
 */
define([
    'logging'
], function(logging) {
    var log = logging.getLogger('patterns');
    return log;
});
