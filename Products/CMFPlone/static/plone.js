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
  'mockup-patterns-autotoc',
  'mockup-patterns-cookietrigger',
  'mockup-patterns-formunloadalert',
  'mockup-patterns-preventdoublesubmit',
  'mockup-patterns-formautofocus',
  'mockup-patterns-markspeciallinks',
  'mockup-patterns-navigationmarker',
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
  if ((window.parent === window) ||
      (window.frameElement.nodeName === 'IFRAME')) {
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

  // TODO: Needs to be moved to controlpanel js as well
  $(document).ready(function() {
      function autohide_quality_fields(animate) {
        var highpixeldensity = $('#form-widgets-highpixeldensity_scales option:selected').attr('value');
        var quality_2x = $('div[data-fieldname="form.widgets.quality_2x"]');
        var quality_3x = $('div[data-fieldname="form.widgets.quality_3x"]');

        if (highpixeldensity == 'disabled') {
            quality_2x.fadeOut();
            quality_3x.fadeOut();
        }
        else if (highpixeldensity == '2x') {
            quality_2x.fadeIn();
            quality_3x.fadeOut();
        }
        else if (highpixeldensity == '3x') {
            quality_2x.fadeIn();
            quality_3x.fadeIn();
        }
    }

    if ($('#ImagingSettings')) {
        $('div[data-fieldname="form.widgets.quality_2x"]').hide();
        $('div[data-fieldname="form.widgets.quality_3x"]').hide();
        autohide_quality_fields();
        var select = $('#form-widgets-highpixeldensity_scales');
        select.change(autohide_quality_fields);
    }
  });

});
