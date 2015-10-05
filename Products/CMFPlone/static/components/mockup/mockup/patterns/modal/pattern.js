/* Modal pattern.
 *
 * Options:
 *    height(string): Set the height of the modal, for example: 250px ('')
 *    width(string): Set the width of the modal, for example: 80% or 500px. ('')
 *    margin(function or integer): A function, Integer or String which will be used to set the margin of the modal in pixels. If a function is passed it must return an Integer. (20)
 *    position(string): Position the modal relative to the window with the format: "<horizontal> <vertical>" -- allowed values: top, bottom, left, right, center, middle. ('center middle')
 *    triggers(array): Add event listeners to elements on the page which will open the modal when triggered. Pass an Array of strings with the format ["&lt;event&gt; &lt;selector&gt;"] or ["&lt;event&gt;"]. For example, ["click .someButton"]. If you pass in only an event such as, ["change"], the event listener will be added to the element on which the modal was initiated, usually a link or button. ([])
 *    title(string): A string to place in the modal header. If title is provided, titleSelector is not used. (null)
 *    titleSelector(string): Selector for an element to extract from the content provided to the modal and place in the modal header. ('h1:first')
 *    content(string): Selector for an element within the content provided to the modal to use as the modal body. ('#content')
 *    prependContent(string): Selector for elements within the content provided to the modal which will be collected and inserted, by default above, the modal content. This is useful for extracting things like alerts or status messages on forms and displaying them to the user after an AJAX response. ('.portalMessage')
 *    backdrop(string): Selector for the element upon which the Backdrop pattern should be initiated. The Backdrop is a full width mask that will be apply above the content behind the modal which is useful for highlighting the modal dialog to the user. ('body')
 *    backdropOptions(object): Look at options at backdrop pattern. ({ zIndex: "1040", opacity: "0.8", className: "backdrop", classActiveName: "backdrop-active", closeOnEsc: true, closeOnClick: true })
 *    buttons(string): Selector for matching elements, usually buttons, inputs or links, from the modal content to place in the modal footer. The original elements in the content will be hidden. ('.formControls > input[type="submit"]')
 *    automaticallyAddButtonActions(boolean): Automatically create actions for elements matched with the buttons selector. They will use the options provided in actionOptions. (true)
 *    loadLinksWithinModal(boolean): Automatically load links inside of the modal using AJAX. (true)
 *    actionOptions(object): A hash of selector to options. Where options can include any of the defaults from actionOptions. Allows for the binding of events to elements in the content and provides options for handling ajax requests and displaying them in the modal. ({})
 *
 *
 * Documentation:
 *    # Example
 *
 *    {{ example-basic }}
 *
 *    {{ example-long }}
 *
 *    {{ example-tinymce }}
 *
 *
 * Example: example-basic
 *    <a href="#modal1" class="plone-btn plone-btn-large plone-btn-primary pat-plone-modal"
 *                      data-pat-plone-modal="width: 400">Modal basic</a>
 *    <div id="modal1" style="display: none">
 *      <h1>Basic modal!</h1>
 *      <p>Indeed. Whoa whoa whoa whoa. Wait.</p>
 *    </div>
 *
 * Example: example-long
 *    <a href="#modal2" class="plone-btn plone-btn-lg plone-btn-primary pat-plone-modal"
 *                      data-pat-plone-modal="width: 500">Modal long scrolling</a>
 *    <div id="modal2" style="display: none">
 *      <h1>Basic with scrolling</h1>
 *      <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua</p>
 *      <br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br />
 *      <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua</p>
 *      <br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br />
 *      <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua</p>
 *      <br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br />
 *      <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua</p>
 *      <br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br />
 *      <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua</p>
 *      <br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br />
 *      <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua</p>
 *    </div>
 *
 *
 * Example: example-tinymce
 *    <a href="#modaltinymce" class="btn btn-lg btn-primary pat-plone-modal"
 *       data-pat-plone-modal="height: 600px;
 *                       width: 80%">
 *       Modal with TinyMCE</a>
 *    <div id="modaltinymce" style="display:none">
 *      <textarea class="pat-tinymce"></textarea>
 *    </div>
 *
 */

define([
  'jquery',
  'underscore',
  'mockup-patterns-base',
  'mockup-patterns-backdrop',
  'pat-registry',
  'mockup-router',
  'mockup-utils',
  'translate',
  'jquery.form'
], function($, _, Base, Backdrop, registry, Router, utils, _t) {
  'use strict';

  var Modal = Base.extend({
    name: 'plone-modal',
    trigger: '.pat-plone-modal',
    createModal: null,
    $model: null,
    defaults: {
      width: '',
      height: '',
      margin: 20,
      position: 'center middle', // format: '<horizontal> <vertical>' -- allowed values: top, bottom, left, right, center, middle
      triggers: [],
      backdrop: 'body', // Element to initiate the Backdrop on.
      backdropOptions: {
        zIndex: '1040',
        opacity: '0.85',
        className: 'plone-modal-backdrop',
        classActiveName: 'plone-backdrop-active',
        closeOnEsc: true,
        closeOnClick: true
      },
      title: null,
      titleSelector: 'h1:first',
      buttons: '.formControls > input[type="submit"]',
      content: '#content',
      automaticallyAddButtonActions: true,
      loadLinksWithinModal: true,
      prependContent: '.portalMessage',
      templateOptions: {
        className: 'plone-modal fade',
        classDialog: 'plone-modal-dialog',
        classModal: 'plone-modal-content',
        classHeaderName: 'plone-modal-header',
        classBodyName: 'plone-modal-body',
        classFooterName: 'plone-modal-footer',
        classWrapperName: 'plone-modal-wrapper',
        classWrapperInnerName: 'modal-wrapper-inner',
        classActiveName: 'in',
        classPrependName: '', // String, css class to be applied to the wrapper of the prepended content
        classContentName: '',  // String, class name to be applied to the content of the modal, useful for modal specific styling
        template: '' +
          '<div class="<%= options.className %>">' +
          '  <div class="<%= options.classDialog %>">' +
          '    <div class="<%= options.classModal %>">' +
          '      <div class="<%= options.classHeaderName %>">' +
          '        <a class="plone-modal-close">&times;</a>' +
          '        <% if (title) { %><h2 class="plone-modal-title"><%= title %></h2><% } %>' +
          '      </div>' +
          '      <div class="<%= options.classBodyName %>">' +
          '        <div class="<%= options.classPrependName %>"><%= prepend %></div> ' +
          '        <div class="<%= options.classContentName %>"><%= content %></div>' +
          '      </div>' +
          '      <div class="<%= options.classFooterName %>"> ' +
          '        <% if (buttons) { %><%= buttons %><% } %>' +
          '      </div>' +
          '    </div>' +
          '  </div>' +
          '</div>'
      },
      actions: {},
      actionOptions: {
        eventType: 'click',
        disableAjaxFormSubmit: false,
        target: null,
        ajaxUrl: null, // string, or function($el, options) that returns a string
        modalFunction: null, // String, function name on self to call
        isForm: false,
        timeout: 5000,
        displayInModal: true,
        reloadWindowOnClose: true,
        error: '.portalMessage.error',
        formFieldError: '.field.error',
        onSuccess: null,
        onError: null,
        onFormError: null,
        onTimeout: null,
        redirectOnResponse: false,
        redirectToUrl: function($action, response, options) {
          var reg;
          reg = /<body.*data-view-url=[\"'](.*)[\"'].*/im.exec(response);
          if (reg && reg.length > 1) {
            // view url as data attribute on body (Plone 5)
            return reg[1].split('"')[0];
          }
          reg = /<body.*data-base-url=[\"'](.*)[\"'].*/im.exec(response);
          if (reg && reg.length > 1) {
            // Base url as data attribute on body (Plone 5)
            return reg[1].split('"')[0];
          }
          reg = /<base.*href=[\"'](.*)[\"'].*/im.exec(response);
          if (reg && reg.length > 1) {
              // base tag available (Plone 4)
              return reg[1];
          }
          return '';
        }
      },
      routerOptions: {
        id: null,
        pathExp: null
      },
      form: function(actions) {
        var self = this;
        var $modal = self.$modal;

        if (self.options.automaticallyAddButtonActions) {
          actions[self.options.buttons] = {};
        }

        if (self.options.loadLinksWithinModal) {
          actions.a = {};
        }

        $.each(actions, function(action, options) {
          var actionKeys = _.union(_.keys(self.options.actionOptions), ['templateOptions']);
          var actionOptions = $.extend(true, {}, self.options.actionOptions, _.pick(options, actionKeys));
          options.templateOptions = $.extend(true, options.templateOptions, self.options.templateOptions);

          var patternKeys = _.union(_.keys(self.options.actionOptions), ['actions', 'actionOptions']);
          var patternOptions = $.extend(true, _.omit(options, patternKeys), self.options);

          $(action, $('.' + options.templateOptions.classBodyName, $modal)).each(function(action) {
            var $action = $(this);
            $action.on(actionOptions.eventType, function(e) {
              e.stopPropagation();
              e.preventDefault();

              self.loading.show(false);

              // handle event on $action using a function on self
              if (actionOptions.modalFunction !== null) {
                self[actionOptions.modalFunction]();
              // handle event on input/button using jquery.form library
              } else if ($.nodeName($action[0], 'input') || $.nodeName($action[0], 'button') || options.isForm === true) {
                self.options.handleFormAction.apply(self, [$action, actionOptions, patternOptions]);
              // handle event on link with jQuery.ajax
              } else if (options.ajaxUrl !== null || $.nodeName($action[0], 'a')) {
                self.options.handleLinkAction.apply(self, [$action, actionOptions, patternOptions]);
              }

            });
          });
        });
      },
      handleFormAction: function($action, options, patternOptions) {
        var self = this;

        // pass action that was clicked when submiting form
        var extraData = {};
        extraData[$action.attr('name')] = $action.attr('value');

        var $form;

        if ($.nodeName($action[0], 'form')) {
          $form = $action;
        } else {
          $form = $action.parents('form:not(.disableAutoSubmit)');
        }

        var url;
        if (options.ajaxUrl !== null) {
          if (typeof options.ajaxUrl === 'function') {
            url = options.ajaxUrl.apply(self, [$action, options]);
          } else {
            url = options.ajaxUrl;
          }
        } else {
          url = $action.parents('form').attr('action');
        }

        if(options.disableAjaxFormSubmit){
          if($action.attr('name') && $action.attr('value')){
            $form.append($('<input type="hidden" name="' + $action.attr('name') + '" value="' + $action.attr('value') + '" />'));
          }
          $form.trigger('submit');
          return;
        }
        // We want to trigger the form submit event but NOT use the default
        $form.on('submit', function(e) {
          e.preventDefault();
        });
        $form.trigger('submit');

        self.loading.show(false);
        $form.ajaxSubmit({
          timeout: options.timeout,
          data: extraData,
          url: url,
          error: function(xhr, textStatus, errorStatus) {
            self.loading.hide();
            if (textStatus === 'timeout' && options.onTimeout) {
              options.onTimeout.apply(self, xhr, errorStatus);
            // on "error", "abort", and "parsererror"
            } else if (options.onError) {
              options.onError(xhr, textStatus, errorStatus);
            } else {
              window.alert(_t('There was an error submitting the form.'));
              console.log('error happened do something');
            }
            self.emit('formActionError', [xhr, textStatus, errorStatus]);
          },
          success: function(response, state, xhr, form) {
            self.loading.hide();
            // if error is found (NOTE: check for both the portal errors
            // and the form field-level errors)
            if ($(options.error, response).size() !== 0 ||
                $(options.formFieldError, response).size() !== 0) {
              if (options.onFormError) {
                options.onFormError(self, response, state, xhr, form);
              } else {
                self.redraw(response, patternOptions);
              }
              return;
            }

            if (options.redirectOnResponse === true) {
              if (typeof options.redirectToUrl === 'function') {
                window.parent.location.href = options.redirectToUrl.apply(self, [$action, response, options]);
              } else {
                window.parent.location.href = options.redirectToUrl;
              }
              return; // cut out right here since we're changing url
            }

            if (options.onSuccess) {
              options.onSuccess(self, response, state, xhr, form);
            }

            if (options.displayInModal === true) {
              self.redraw(response, patternOptions);
            } else {
              $action.trigger('destroy.plone-modal.patterns');
              // also calls hide
              if (options.reloadWindowOnClose) {
                self.reloadWindow();
              }
            }
            self.emit('formActionSuccess', [response, state, xhr, form]);
          }
        });
      },
      handleLinkAction: function($action, options, patternOptions) {
        var self = this;
        var url;

        // Figure out URL
        if (options.ajaxUrl) {
          if (typeof options.ajaxUrl === 'function') {
            url = options.ajaxUrl.apply(self, [$action, options]);
          } else {
            url = options.ajaxUrl;
          }
        } else {
          url = $action.attr('href');
        }

        // Non-ajax link (I know it says "ajaxUrl" ...)
        if (options.displayInModal === false) {
          window.parent.location.href = url;
          return;
        }

        // ajax version
        $.ajax({
          url: url
        }).fail(function(xhr, textStatus, errorStatus) {
          if (textStatus === 'timeout' && options.onTimeout) {
            options.onTimeout(self.$modal, xhr, errorStatus);

          // on "error", "abort", and "parsererror"
          } else if (options.onError) {
            options.onError(xhr, textStatus, errorStatus);
          } else {
            window.alert(_t('There was an error loading modal.'));
          }
          self.emit('linkActionError', [xhr, textStatus, errorStatus]);
        }).done(function(response, state, xhr) {
          self.redraw(response, patternOptions);
          if (options.onSuccess) {
            options.onSuccess(self, response, state, xhr);
          }
          self.emit('linkActionSuccess', [response, state, xhr]);
        }).always(function(){
          self.loading.hide();
        });
      },
      render: function(options) {
        var self = this;

        self.emit('before-render');

        if (!self.$raw) {
          return;
        }
        var $raw = self.$raw.clone();
        // fix for IE9 bug (see http://bugs.jquery.com/ticket/10550)
        $('input:checked', $raw).each(function() {
          if (this.setAttribute) {
            this.setAttribute('checked', 'checked');
          }
        });

        // Object that will be passed to the template
        var tplObject = {
          title: '',
          prepend: '<div />',
          content: '',
          buttons: '<div class="pattern-modal-buttons"></div>',
          options: options.templateOptions
        };

        // setup the Title
        if (options.title === null) {
          var $title = $(options.titleSelector, $raw);
          tplObject.title = $title.html();
          $(options.titleSelector, $raw).remove();
        } else {
          tplObject.title = options.title;
        }

        // Grab items to to insert into the prepend area
        if (options.prependContent) {
          tplObject.prepend = $('<div />').append($(options.prependContent, $raw).clone()).html();
          $(options.prependContent, $raw).remove();
        }

        // Filter out the content if there is a selector provided
        if (options.content) {
          tplObject.content = $(options.content, $raw).html();
        } else {
          tplObject.content = $raw.html();
        }

        // Render html
        self.$modal = $(_.template(self.options.templateOptions.template, tplObject));
        self.$modalDialog = $('> .' + self.options.templateOptions.classDialog, self.$modal);
        self.$modalContent = $('> .' + self.options.templateOptions.classModal, self.$modalDialog);

        // In most browsers, when you hit the enter key while a form element is focused
        // the browser will trigger the form 'submit' event.  Google Chrome also does this,
        // but not when when the default submit button is hidden with 'display: none'.
        // The following code will work around this issue:
        $('form', self.$modal).on ('keydown', function (event) {
          // ignore keys which are not enter, and ignore enter inside a textarea.
          if (event.keyCode !== 13 || event.target.nodeName === 'TEXTAREA') {
            return;
          }
          event.preventDefault();
          $('input[type=submit], button[type=submit], button:not(type)', this).eq(0).trigger('click');
        });

        // Setup buttons
        $(options.buttons, self.$modal).each(function() {
          var $button = $(this);
          $button
            .on('click', function(e) {
              e.stopPropagation();
              e.preventDefault();
            })
            .clone()
            .appendTo($('.pattern-modal-buttons', self.$modal))
            .off('click').on('click', function(e) {
              e.stopPropagation();
              e.preventDefault();
              $button.trigger('click');
            });
          $button.hide();
        });

        self.emit('before-events-setup');

        // Wire up events
        $('.plone-modal-header > a.plone-modal-close, .plone-modal-footer > a.plone-modal-close', self.$modal)
          .off('click')
          .on('click', function(e) {
            e.stopPropagation();
            e.preventDefault();
            $(e.target).trigger('destroy.plone-modal.patterns');
          });

        // cleanup html
        $('.row', self.$modal).removeClass('row');

        // form
        if (options.form) {
          options.form.apply(self, [options.actions]);
        }

        self.$modal
          .addClass(self.options.templateOptions.className)
          .on('click', function(e) {
            e.stopPropagation();
            if ($.nodeName(e.target, 'a')) {
              e.preventDefault();

              // TODO: open links inside modal
              // and slide modal body
            }
            self.$modal.trigger('modal-click');
          })
          .on('destroy.plone-modal.patterns', function(e) {
            e.stopPropagation();
            self.hide();
          })
          .on('resize.plone-modal.patterns', function(e) {
            e.stopPropagation();
            e.preventDefault();
            self.positionModal();
          })
          .appendTo(self.$wrapperInner);
        self.$modal.data('pattern-' + self.name, self);

        self.emit('after-render');
      }
    },
    reloadWindow: function() {
      window.parent.location.reload();
    },
    init: function() {
      var self = this;

      self.backdrop = new Backdrop(
          self.$el.parents(self.options.backdrop),
          self.options.backdropOptions);

      self.$wrapper = $('> .' + self.options.templateOptions.classWrapperName, self.backdrop.$el);
      if (self.$wrapper.size() === 0) {
        var zIndex = self.options.backdropOptions.zIndex !== null ? parseInt(self.options.backdropOptions.zIndex, 10) + 1 : 1041;
        self.$wrapper = $('<div/>')
          .hide()
          .css({
            'z-index': zIndex,
            'overflow-y': 'auto',
            'position': 'fixed',
            'height': '100%',
            'width': '100%',
            'bottom': '0',
            'left': '0',
            'right': '0',
            'top': '0'
          })
          .addClass(self.options.templateOptions.classWrapperName)
          .insertBefore(self.backdrop.$backdrop)
          .on('click', function(e) {
            e.stopPropagation();
            e.preventDefault();
            if (self.options.backdropOptions.closeOnClick) {
              self.backdrop.hide();
            }
          });
      }

      // Router
      if (self.options.routerOptions.id !== null) {
        Router.addRoute('modal', self.options.routerOptions.id, function() {
          this.show();
        }, self, self.options.routerOptions.pathExp, self.options.routerOptions.expReplace);
      }

      self.backdrop.on('hidden', function(e) {
        if (self.$modal !== undefined && self.$modal.hasClass(self.options.templateOptions.classActiveName)) {
          self.hide();
        }
      });

      if (self.options.backdropOptions.closeOnEsc === true) {
        $(document).on('keydown', function(e, data) {
          if (self.$el.is('.' + self.options.templateOptions.classActiveName)) {
            if (e.keyCode === 27) {  // ESC key pressed
              self.hide();
            }
          }
        });
      }

      self.$wrapperInner = $('> .' + self.options.templateOptions.classWrapperInnerName, self.$wrapper);
      if (self.$wrapperInner.size() === 0) {
        self.$wrapperInner = $('<div/>')
          .addClass(self.options.classWrapperInnerName)
          .css({
            'position': 'absolute',
            'bottom': '0',
            'left': '0',
            'right': '0',
            'top': '0'
          })
          .appendTo(self.$wrapper);
      }

      self.loading = new utils.Loading({
        backdrop: self.backdrop
      });

      $(window.parent).resize(function() {
        self.positionModal();
      });

      if (self.options.triggers) {
        $.each(self.options.triggers, function(i, item) {
          var e = item.substring(0, item.indexOf(' '));
          var selector = item.substring(item.indexOf(' '), item.length);
          $(selector || self.$el).on(e, function(e) {
            e.stopPropagation();
            e.preventDefault();
            self.show();
          });
        });
      }

      if (self.$el.is('a')) {
        if (self.$el.attr('href') && !self.options.image) {
          if (!self.options.target && self.$el.attr('href').substr(0, 1) === '#') {
            self.options.target = self.$el.attr('href');
            self.options.content = '';
          }
          if (!self.options.ajaxUrl && self.$el.attr('href').substr(0, 1) !== '#') {
            self.options.ajaxUrl = self.$el.attr('href');
          }
        }
        self.$el.on('click', function(e) {
          e.stopPropagation();
          e.preventDefault();
          self.show();
        });
      }
      self.initModal();
    },

    createAjaxModal: function() {
      var self = this;
      self.emit('before-ajax');
      self.loading.show();
      self.ajaxXHR = $.ajax({
        url: self.options.ajaxUrl,
        type: self.options.ajaxType
      }).done(function(response, textStatus, xhr) {
        self.ajaxXHR = undefined;
        self.$raw = $('<div />').append($(utils.parseBodyTag(response)));
        self.emit('after-ajax', self, textStatus, xhr);
        self._show();
      }).fail(function(xhr, textStatus, errorStatus){
        var options = self.options.actionOptions;
        if (textStatus === 'timeout' && options.onTimeout) {
          options.onTimeout(self.$modal, xhr, errorStatus);
        } else if (options.onError) {
          options.onError(xhr, textStatus, errorStatus);
        } else {
          window.alert(_t('There was an error loading modal.'));
          self.hide();
        }
        self.emit('linkActionError', [xhr, textStatus, errorStatus]);
      }).always(function(){
        self.loading.hide();
      });
    },

    createTargetModal: function() {
      var self = this;
      self.$raw = $(self.options.target).clone();
      self._show();
    },

    createBasicModal: function() {
      var self = this;
      self.$raw = $('<div/>').html(self.$el.clone());
      self._show();
    },

    createHtmlModal: function() {
      var self = this;
      var $el = $(self.options.html);
      self.$raw = $el;
      self._show();
    },

    createImageModal: function(){
      var self = this;
      self.$wrapper.addClass('image-modal');
      var src = self.$el.attr('href');
      // XXX aria?
      self.$raw = $('<div><h1>Image</h1><div id="content"><div class="modal-image"><img src="' + src + '" /></div></div></div>');
      self._show();
    },

    initModal: function() {
      var self = this;
      if (self.options.ajaxUrl) {
        self.createModal = self.createAjaxModal;
      } else if (self.options.target) {
        self.createModal = self.createTargetModal;
      } else if (self.options.html) {
        self.createModal = self.createHtmlModal;
      } else if (self.options.image){
        self.createModal = self.createImageModal;
      } else {
        self.createModal = self.createBasicModal;
      }
    },

    findPosition: function(horpos, vertpos, margin, modalWidth, modalHeight,
                           wrapperInnerWidth, wrapperInnerHeight) {
      var returnpos = {};
      var absTop, absBottom, absLeft, absRight;
      absRight = absLeft = absTop = absLeft = 'auto';

      // -- HORIZONTAL POSITION -----------------------------------------------
      if (horpos === 'left') {
        absLeft = margin + 'px';
        // if the width of the wrapper is smaller than the modal, and thus the
        // screen is smaller than the modal, force the left to simply be 0
        if (modalWidth > wrapperInnerWidth) {
          absLeft = '0px';
        }
        returnpos.left = absLeft;
      }
      else if (horpos === 'right') {
        absRight =  margin + 'px';
        // if the width of the wrapper is smaller than the modal, and thus the
        // screen is smaller than the modal, force the right to simply be 0
        if (modalWidth > wrapperInnerWidth) {
          absRight = '0px';
        }
        returnpos.right = absRight;
        returnpos.left = 'auto';
      }
      // default, no specified location, is to center
      else {
        absLeft = ((wrapperInnerWidth / 2) - (modalWidth / 2) - margin) + 'px';
        // if the width of the wrapper is smaller than the modal, and thus the
        // screen is smaller than the modal, force the left to simply be 0
        if (modalWidth > wrapperInnerWidth) {
          absLeft = '0px';
        }
        returnpos.left = absLeft;
      }

      // -- VERTICAL POSITION -------------------------------------------------
      if (vertpos === 'top') {
        absTop = margin + 'px';
        // if the height of the wrapper is smaller than the modal, and thus the
        // screen is smaller than the modal, force the top to simply be 0
        if (modalHeight > wrapperInnerHeight) {
          absTop = '0px';
        }
        returnpos.top = absTop;
      }
      else if (vertpos === 'bottom') {
        absBottom = margin + 'px';
        // if the height of the wrapper is smaller than the modal, and thus the
        // screen is smaller than the modal, force the bottom to simply be 0
        if (modalHeight > wrapperInnerHeight) {
          absBottom = '0px';
        }
        returnpos.bottom = absBottom;
        returnpos.top = 'auto';
      }
      else {
        // default case, no specified location, is to center
        absTop = ((wrapperInnerHeight / 2) - (modalHeight / 2) - margin) + 'px';
        // if the height of the wrapper is smaller than the modal, and thus the
        // screen is smaller than the modal, force the top to simply be 0
        if (modalHeight > wrapperInnerHeight) {
          absTop = '0px';
        }
        returnpos.top = absTop;
      }

      return returnpos;
    },
    modalInitialized: function() {
      var self = this;
      return self.$modal !== null && self.$modal !== undefined;
    },
    // re-position modal at any point.
    //
    // Uses:
    //  options.margin
    //  options.width
    //  options.height
    //  options.position
    positionModal: function() {
      var self = this;

      // modal isn't initialized
      if (!self.modalInitialized()) { return; }

      // clear out any previously set styling
      self.$modal.removeAttr('style');

      // make sure the (inner) wrapper fills it's container
      //self.$wrapperInner.css({height:'100%', width:'100%'});

      // if backdrop wrapper is set on body, then wrapper should have height of
      // the window, so we can do scrolling of inner wrapper
      if (self.$wrapper.parent().is('body')) {
        self.$wrapper.height($(window.parent).height());
      }

      var margin = typeof self.options.margin === 'function' ? self.options.margin() : self.options.margin;
      self.$modal.css({
        'position': 'absolute',
        'padding': margin
      });
      self.$modalDialog.css({
        margin: '0',
        padding: '0',
        width: self.options.width, // defaults to "", which doesn't override other css
        height: self.options.height // defaults to "", which doesn't override other css
      });
      self.$modalContent.css({
        width: self.options.width, // defaults to "", which doesn't override other css
      });

      var posopt = self.options.position.split(' '),
          horpos = posopt[0],
          vertpos = posopt[1];
      var modalWidth = self.$modalDialog.outerWidth(true);
      var modalHeight = self.$modalDialog.outerHeight(true);
      var wrapperInnerWidth = self.$wrapperInner.width();
      var wrapperInnerHeight = self.$wrapperInner.height();

      var pos = self.findPosition(
        horpos, vertpos, margin, modalWidth, modalHeight,
        wrapperInnerWidth, wrapperInnerHeight
      );
      for (var key in pos) {
        self.$modalDialog.css(key, pos[key]);
      }
    },
    render: function(options) {
      var self = this;
      self.emit('render');
      self.options.render.apply(self, [options]);
      self.emit('rendered');
    },
    show: function() {
      var self = this;
      self.createModal();
    },
    _show: function() {
      var self = this;
      self.render.apply(self, [ self.options ]);
      self.emit('show');
      self.backdrop.show();
      self.$wrapper.show();
      self.loading.hide();
      self.$wrapper.parent().css('overflow', 'hidden');
      self.$el.addClass(self.options.templateOptions.classActiveName);
      self.$modal.addClass(self.options.templateOptions.classActiveName);
      registry.scan(self.$modal);
      self.positionModal();
      $('img', self.$modal).load(function() {
        self.positionModal();
      });
      $(window.parent).on('resize.plone-modal.patterns', function() {
        self.positionModal();
      });
      $('body').addClass('plone-modal-open');
      self.emit('shown');
    },
    hide: function() {
      var self = this;
      if (self.ajaxXHR) {
        self.ajaxXHR.abort();
      }
      self.emit('hide');
      if (self._suppressHide) {
        if (!window.confirm(self._suppressHide)) {
          return;
        }
      }
      if ($('.plone-modal', self.$wrapper).size() < 2) {
        self.backdrop.hide();
        self.$wrapper.hide();
        self.$wrapper.parent().css('overflow', 'visible');
        $('body').removeClass('plone-modal-open');
      }
      self.loading.hide();
      self.$el.removeClass(self.options.templateOptions.classActiveName);
      if (self.$modal !== undefined) {
        self.$modal.remove();
        self.initModal();
      }
      $(window.parent).off('resize.plone-modal.patterns');
      self.emit('hidden');
    },
    redraw: function(response, options) {
      var self = this;
      self.emit('beforeDraw');
      self.$modal.remove();
      self.$raw = $('<div />').append($(utils.parseBodyTag(response)));
      self.render.apply(self, [options || self.options]);
      self.$modal.addClass(self.options.templateOptions.classActiveName);
      self.positionModal();
      registry.scan(self.$modal);
      self.emit('afterDraw');
    }
  });

  return Modal;

});
