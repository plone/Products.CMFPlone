// Copyright (C) 2010 Plone Foundation
//
// This program is free software; you can redistribute it and/or modify it
// under the terms of the GNU General Public License as published by the Free
// Software Foundation; either version 2 of the License.
//
// This program is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
// FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
// more details.
//
// You should have received a copy of the GNU General Public License along with
// this program; if not, write to the Free Software Foundation, Inc., 51
// Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
//

if (window.jQuery) {
  define( 'jquery', [], function () {
    'use strict';
    return window.jQuery;
  } );
}

require([
  'jquery',
  'pat-registry',
  'mockup-patterns-base',

  'mockup-patterns-select2',
  'mockup-patterns-pickadate',
  'plone-patterns-toolbar',
  'mockup-patterns-autotoc',
  'mockup-patterns-cookietrigger',
  'mockup-patterns-formunloadalert',
  'mockup-patterns-preventdoublesubmit',
  'mockup-patterns-formautofocus',
  'mockup-patterns-markspeciallinks',
  'mockup-patterns-modal',
  'mockup-patterns-livesearch',
  'mockup-patterns-contentloader',
  'mockup-patterns-moment',
  'bootstrap-dropdown',
  'bootstrap-collapse',
  'bootstrap-tooltip',
], function($, registry, Base) {
  'use strict';

  // initialize only if we are in top frame
  if (window.parent === window) {
    $(document).ready(function() {
      $('body').addClass('pat-plone');
      if (!registry.initialized) {
        registry.init();
      }
    });
  }

  // TODO: Needs to be moved to controlpanel js
  $(document).ready(function() {
    var cookieNegotiation = (
      $("#form-widgets-use_cookie_negotiation > input").value === 'selected');
    if (cookieNegotiation !== true) {
      $("#formfield-form-widgets-authenticated_users_only").hide();
    }else{
      $("#formfield-form-widgets-authenticated_users_only").show();
    }
  });

});
