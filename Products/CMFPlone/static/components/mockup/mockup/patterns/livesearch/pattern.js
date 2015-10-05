/* Livesearch
 *
 * Options:
 *    ajaxUrl(string): JSON search url
 *    perPage(integer): results per page, defaults to 7
 *    quietMillis: how long to wait after type stops before sending out request in milliseconds. Defaults to 350
 *    minimumInputLength: miniumum number of letters before doing search. Defaults to 3
 *    inputSelector: css select to input element search is done with. Defaults to input[type="text"]
 *    itemTemplate: override template used to render item results
 *
 * Documentation:
 *   # General
 *
 *   # Default
 *
 *   {{ example-1 }}
 *
 * Example: example-1
 *    <form action="search" class="pat-livesearch" data-pat-livesearch="ajaxUrl:livesearch.json">
 *      <input type="text" />
 *    </form>
 *
 */

define([
  'jquery',
  'mockup-patterns-base',
  'underscore',
  'translate'
], function ($, Base, _, _t){
  'use strict';

  var Livesearch = Base.extend({
    name: 'livesearch',
    trigger: '.pat-livesearch',
    timeout: null,
    active: false,
    results: null,
    selectedItem: -1,
    resultsClass: 'livesearch-results',
    defaults: {
      ajaxUrl: null,
      perPage: 7,
      quietMillis: 350,
      minimumInputLength: 4,
      inputSelector: 'input[type="text"]',
      itemTemplate: '<li class="search-result <%- state %>">' +
        '<h4 class="title"><a href="<%- url %>"><%- title %></a></h4>' +
        '<p class="description"><%- description %></p>' +
      '</li>',
    },
    doSearch: function(page){
      var self = this;
      self.active = true;
      self.render();
      self.$el.addClass('searching');
      var query = self.$el.serialize();
      if(page === undefined){
        page = 1;
      }
      $.ajax({
        url: self.options.ajaxUrl + '?' + query +
             '&page=' + page +
             '&perPage=' + self.options.perPage,
        dataType: 'json'
      }).done(function(data){
        self.results = data;
        self.page = page;
        // maybe odd here.. but we're checking to see if the user
        // has typed while a search was being performed. Perhap another search if so
        if(query !== self.$el.serialize()){
          self.doSearch();
        }
      }).fail(function(){
        self.results = {
          items: [{
            url: '',
            title: _t('Error'),
            description: _t('There was an error searching…'),
            state: 'error',
            error: false
          }],
          total: 1
        };
        self.page = 1;
      }).always(function(){
        self.active = false;
        self.selectedItem = -1;
        self.$el.removeClass('searching');
        self.render();
      });
    },
    render: function(){
      var self = this;
      self.$results.empty();

      /* find a status message */

      if(self.active){
        self.$results.append($('<li class="searching">' + _t('searching…') + '</li>'));
      }else if(self.results === null){
        // no results gathered yet
        self.$results.append($('<li class="no-results no-search">' + _t('enter search phrase') + '</li>'));
      } else if(self.results.total === 0){
        self.$results.append($('<li class="no-results">' + _t('no results found') + '</li>'));
      } else{
        self.$results.append($('<li class="results-summary">' + _t('found') +
                               ' ' + self.results.total + ' ' + _t('results') + '</li>'));
      }

      if(self.results !== null){
        var template = _.template(self.options.itemTemplate);
        _.each(self.results.items, function(item, index){
          var $el = $(template($.extend({_t: _t}, item)));
          $el.attr('data-url', item.url).on('click', function(){
            if(!item.error){
              window.location = item.url;
            }
          });
          if(index === self.selectedItem){
            $el.addClass('selected');
          }
          self.$results.append($el);
        });
        var nav = [];
        if(self.page > 1){
          var $prev = $('<a href="#" class="prev">' + _t('Previous') + '</a>');
          $prev.click(function(e){
            self.disableHiding = true;
            e.preventDefault();
            self.doSearch(self.page - 1);
          });
          nav.push($prev);
        }
        if((self.page * self.options.perPage) < self.results.total){
          var $next = $('<a href="#" class="next">' + _t('Next') + '</a>');
          $next.click(function(e){
            self.disableHiding = true;
            e.preventDefault();
            self.doSearch(self.page + 1);
          });
          nav.push($next);
        }
        if(nav.length > 0){
          var $li = $('<li class="load-more"><div class="page">' + self.page + '</div></li>');
          $li.prepend(nav);
          self.$results.append($li);
        }
      }
      self.position();
    },
    position: function(){
      /* we are positioning directly below the
         input box, same width */
      var self = this;

      self.$el.addClass('livesearch-active');
      var pos = self.$input.position();
      self.$results.width(self.$el.outerWidth());
      self.$results.css({
        top: pos.top + self.$input.outerHeight(),
        left: pos.left
      });
      self.$results.show();
    },
    hide: function(){
      this.$results.hide();
      this.$el.removeClass('livesearch-active');
    },
    init: function(){
      var self = this;

      self.$input = self.$el.find(self.options.inputSelector);
      self.$input.off('focusout').on('focusout', function(){
        /* we put this in a timer so click events still
           get trigger on search results */
        setTimeout(function(){
          /* hack, look above, to handle dealing with clicks
             unfocusing element */
          if(!self.disableHiding){
            self.hide();
          }else{
            self.disableHiding = false;
            // and refocus elemtn
            self.$input.focus();
          }
        }, 200);
      }).off('focusin').on('focusin', function(){
        if(!self.onceFocused){
          /* Case: field already filled out but no reasons
             present yet, do ajax search and grab some results */
          self.onceFocused = true;
          if(self.$input.val().length >= self.options.minimumInputLength){
            self.doSearch();
          }
        } else if(!self.$results.is(':visible')){
          self.render();
        }
      }).attr('autocomplete', 'off').off('keyup').on('keyup', function(e){
        // first off, we're capturing up, down and enter key presses
        if(self.results && self.results.items && self.results.items.length > 0){
          var code = e.keyCode || e.which;
          if(code === 13){
            /* enter key, check to see if there is a selected item */
            if(self.selectedItem !== -1){
              window.location = self.results.items[self.selectedItem].url;
            }
            return;
          } else if(code === 38){
            /* up key */
            if(self.selectedItem !== -1){
              self.selectedItem -= 1;
              self.render();
            }
            return;
          } else if(code === 40){
            /* down key */
            if(self.selectedItem < self.results.items.length){
              self.selectedItem += 1;
              self.render();
            }
            return;
          }
        }

        /* then, we handle timeouts for doing ajax search */
        if(self.timeout !== null){
          clearTimeout(self.timeout);
          self.timeout = null;
        }
        if(self.active){
          return;
        }
        if(self.$input.val().length >= self.options.minimumInputLength){
          self.timeout = setTimeout(function(){
            self.doSearch();
          }, self.options.quietMillis);
        }else{
          self.results = null;
          self.render();
        }
      });

      /* create result dom */
      self.$results = $('<ul class="' + self.resultsClass + '"></ul>').hide().insertAfter(self.$input);
    }
  });

  return Livesearch;
});
