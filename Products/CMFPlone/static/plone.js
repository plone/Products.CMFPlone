// Author: Rok Garbas
// Contact: rok@garbas.si
// Version: 1.0
// Description:
//
// License:
//
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

require([
  'jquery',
  'mockup-registry',
  'mockup-patterns-base',

  'mockup-patterns-textareamimetypeselector',
  'mockup-patterns-select2',
  'mockup-patterns-pickadate',
  'mockup-patterns-relateditems',
  'mockup-patterns-querystring',
  'mockup-patterns-tinymce',
  'plone-patterns-toolbar',
  'mockup-patterns-accessibility',
  'mockup-patterns-autotoc',
  'mockup-patterns-cookietrigger',
  'mockup-patterns-formunloadalert',
  'mockup-patterns-preventdoublesubmit',
  'mockup-patterns-inlinevalidation',
  'mockup-patterns-formautofocus',
  'mockup-patterns-modal',
  'mockup-patterns-markspeciallinks',
  'mockup-patterns-structure',
  'bootstrap-dropdown',
  'bootstrap-collapse',
  'bootstrap-tooltip'
], function($, Registry, Base) {
  'use strict';

  // initialize only if we are in top frame
  if (window.parent === window) {
    $(document).ready(function() {
      $('body').addClass('pat-plone');
      Registry.scan($('body'));
    });
  }

});
