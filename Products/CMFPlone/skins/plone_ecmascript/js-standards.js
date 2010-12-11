/* This is an include to set jslint standards for a file. A common
   use would be to run
   
   cat js-standards.js accessibility.js | jslint
   
   to analyze accessibility.js using these standards.
   
   These are the jslint "Good Parts" standards except that:
   
   * Tight white-space checking is off;
   * the "use strict" check is off;
   * browser variables are on;
   * common globals are set.
*/

/*jslint white:false, onevar:true, undef:true, nomen:true, eqeqeq:true, plusplus:true, bitwise:true, regexp:true, newcap:true, immed:true, strict:false, browser:true */
/*global jQuery:false, document:false, window:false, location:false */