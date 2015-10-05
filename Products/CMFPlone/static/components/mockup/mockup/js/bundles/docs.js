require([
  'mockup-docs',
  'text!docs-getting-started',
  'text!docs-learn',
  'text!docs-contribute',
  'bootstrap-collapse',
  'mockup-fakeserver'
], function(Docs, GETTING_STARTED, LEARN, CONTRIBUTE) {
  'use strict';

  var docs = new Docs({
    pages: [
      { id: 'index',
        title: 'Mockup',
        description: 'A collection of client side patterns for faster and easier ' +
                     'web  development',
        text: '[See it in action!](#pattern)',
        autotoc: false
      },
      { id: 'getting-started',
        title: 'Getting Started',
        description: 'How to install and get started with Mockup',
        text: GETTING_STARTED
      },
      { id: 'learn',
        title: 'Learn',
        description: 'How to start developing with Mockup',
        text: LEARN
      },
      { id: 'pattern',
        title: 'Patterns',
        description: 'All the patterns you\'ll ever need',
        autotoc: false,
        patterns: [
          { id: 'autotoc',
            title: 'Autotoc',
            description: 'Automatically generate a table of contents',
            url: 'patterns/autotoc/pattern.js'
          },
          { id: 'backdrop',
            title: 'Backdrop',
            description: 'TODO',
            url: 'patterns/backdrop/pattern.js'
          },
          { id: 'cookietrigger',
            title: 'Cookie Trigger',
            description: "Shows a DOM element if browser cookies are disabled.",
            url: 'patterns/cookietrigger/pattern.js'
          },
          { id: 'formautofocus',
            title: 'Form Auto Focus',
            description: 'TODO',
            url: 'patterns/formautofocus/pattern.js'
          },
          { id: 'formunloadalert',
            title: 'Form Unload Alert',
            description: 'A pattern to warn user when changes are unsaved and they try to navigate away from page',
            url: 'patterns/formunloadalert/pattern.js'
          },
          { id: 'inlinevalidation',
            title: 'Inline Validation',
            description: 'Client side validation of form fields',
            url: 'patterns/inlinevalidation/pattern.js'
          },
          { id: 'markspeciallinks',
            title: 'Mark special links',
            description: 'Mark special links based on protocol and optionally open in new window.',
            url: 'patterns/markspeciallinks/pattern.js'
          },
          { id: 'modal',
            title: 'Modal',
            description: 'Creates a modal dialog (also called overlay)',
            url: 'patterns/modal/pattern.js'
          },
          { id: 'moment',
            title: 'Moment',
            description: 'Human date representation of dates',
            url: 'patterns/moment/pattern.js'
          },
          { id: 'pickadate',
            title: 'Pick-A-Date',
            description: 'Allows the user to select a date (with or without time) through a calendar',
            url: 'patterns/pickadate/pattern.js'
          },
          { id: 'preventdoublesubmit',
            title: 'Prevent Double Submit',
            description: 'A pattern to prevent submitting a form twice',
            url: 'patterns/preventdoublesubmit/pattern.js'
          },
          { id: 'querystring',
            title: 'Querystring',
            description: 'A widget for creating queries for collections',
            url: 'patterns/querystring/pattern.js'
          },
          { id: 'relateditems',
            title: 'Related Items',
            description: 'An advanced widget for selecting related items',
            url: 'patterns/relateditems/pattern.js'
          },
          { id: 'select2',
            title: 'Select2',
            description: 'Autocompletes, multiple or single selections from any kind of data source (with search!)',
            url: 'patterns/select2/pattern.js'
          },
          { id: 'sortable',
            title: 'Sortable',
            description: 'Sort items in list using drag and drop',
            url: 'patterns/sortable/pattern.js'
          },
          { id: 'structure',
            title: 'Structure',
            description: 'Managing a folder of items',
            url: 'patterns/structure/pattern.js'
          },
          { id: 'textareamimetypeselector',
            title: 'Textarea MimeType Selector',
            description: 'Selects the MimeType for a textarea and changes the widget according to the MimeType',
            url: 'patterns/textareamimetypeselector/pattern.js'
          },
          { id: 'tinymce',
            title: 'TinyMCE',
            description: 'Rich text editor',
            url: 'patterns/tinymce/pattern.js'
          },
          { id: 'toggle',
            title: 'Toggle',
            description: 'Toggles any attribute value after some event is fired',
            url: 'patterns/toggle/pattern.js'
          },
          { id: 'tooltip',
            title: 'Tooltip',
            description: 'A pattern to show a tooltip on hover',
            url: 'patterns/tooltip/pattern.js'
          },
          { id: 'tree',
            title: 'Tree',
            description: 'Manage tree of items',
            url: 'patterns/tree/pattern.js'
          },
          { id: 'upload',
            title: 'Upload',
            description: 'File upload with drag and drop support.',
            url: 'patterns/upload/pattern.js'
          },
          { id: 'filemanager',
            title: 'File Manager',
            description: 'Manage file system-like resources',
            url: 'patterns/filemanager/pattern.js'
          },
          { id: 'texteditor',
            title: 'Text editor',
            description: 'Edit files TTW nicely',
            url: 'patterns/texteditor/pattern.js'
          },
          { id: 'thememapper',
            title: 'Theme Mapper',
            description: 'Map theme rules',
            url: 'patterns/thememapper/pattern.js'
          },
          { id: 'resourceregistry',
            title: 'Resource Registry',
            description: 'Register and override resources',
            url: 'patterns/resourceregistry/pattern.js'
          },
          { id: 'eventedit',
            title: 'Event Edit Forms',
            description: 'Start/End delta, validation whole day and open end handling',
            url: 'patterns/eventedit/pattern.js'
          },
          { id: 'livesearch',
            title: 'Live search',
            description: 'Live search widget',
            url: 'patterns/livesearch/pattern.js'
          },
          { id: 'contentloader',
            title: 'Content Loader',
            description: 'Dynamically configure content to be reloaded',
            url: 'patterns/contentloader/pattern.js'
          },
          { id: 'recurrence',
            title: 'Recurrence Widget',
            description: 'Recurrence widget',
            url: 'patterns/recurrence/pattern.js'
          }
        ]
      },
      { id: 'contribute',
        title: 'Contribute',
        description: 'How to start contributing',
        position: 'right',
        text: CONTRIBUTE
      }
    ]

  });

  return docs;
});

