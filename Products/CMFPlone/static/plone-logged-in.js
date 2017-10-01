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
  'mockup-patterns-textareamimetypeselector',
  'mockup-patterns-relateditems',
  'mockup-patterns-querystring',
  'mockup-patterns-tinymce',
  'mockup-patterns-inlinevalidation',
  'mockup-patterns-structure',
  'mockup-patterns-structureupdater',
  'mockup-patterns-recurrence',
  'plone-patterns-portletmanager',
  'plone-patterns-toolbar',
], function() {
  'use strict';
});
