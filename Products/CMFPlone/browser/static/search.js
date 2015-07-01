/* The following line defines global variables defined elsewhere. */
/*globals require*/


if(require === undefined){
  require = function(reqs, torun){
    'use strict';
    return torun(window.jQuery);
  };
}

require([
  'jquery',
], function($) {
  'use strict';

  var $loader = $('.plone-loader');
  if($loader.size() === 0){
    $loader = $('<div class="plone-loader"><div class="loader"/></div>');
    $('body').append($loader);
  }

  var $filter = $('.actionMenu');
  var $filterBtn = $('#search-filter-toggle', $filter);
  var $advSearchInput = $('#advanced-search-input');
  var $ctSelectAll = $('#pt_toggle');
  var $selectAllContainer = $('.search-type-options');
  var $sortingContainer = $('#sorting-options');


  /* handle history */
  if (window.history && window.history.pushState){
    $(window).bind('popstate', function () {
      /* we're just going to cheat and reload the page so
         we aren't keep moving around state here.. 
         Here, I'm lazy, we're not using react here... */
      window.location = window.location.href;
    });
  }

  var pushHistory = function(){
    if(window.history && window.history.pushState){
      var url = window.location.origin + window.location.pathname + '?' + $('#searchform').serialize();
      window.history.pushState(null, null, url);
    }
  };

  var timeout = 0;
  var search = function(){
    $loader.show();
    pushHistory();
    $.ajax({
      url: window.location.origin + window.location.pathname + '?ajax_load=1',
      data: $('#searchform').serialize()
    }).done(function(html){
      var $html = $(html);
      $('#search-results').replaceWith($('#search-results', $html));
      $('#search-term').replaceWith($('#search-term', $html));
      $('#results-count').replaceWith($('#results-count', $html));
      $loader.hide();
    });
  };
  var searchDelayed = function(){
    clearTimeout(timeout);
    timeout = setTimeout(search, 200);
  };

  /* sorting */
  $('a', $sortingContainer).click(function(e){
    e.preventDefault();
    $('a', $sortingContainer).removeClass('active');
    $(this).addClass('active');
    var sort = $(this).attr('data-sort');
    var order = $(this).attr('data-order');
    if(sort){
      $('[name="sort_on"]').attr('value', sort);
      if(order && order == 'reverse'){
        $('[name="sort_order"]').attr('value', 'reverse');
      }
    }else{
      $('[name="sort_on"]').attr('value', '');
      $('[name="sort_order"]').attr('value', '');
    }
    search();
  });


  /* form submission */
  $('.searchPage').submit(function(e){
    e.preventDefault();
    search();
  });


  /* filters */
  $filterBtn.click(function(e){
    e.preventDefault();
    $filter.toggleClass('activated');
    if($filter.hasClass('activated')){
      $advSearchInput.attr('value', 'True');
    }else{
      $advSearchInput.attr('value', 'False');
    }
  });

  $ctSelectAll.change(function(){
    if($ctSelectAll[0].checked){
      $('input', $selectAllContainer).each(function(){
        this.checked = true;
      });
    }else{
      $('input', $selectAllContainer).each(function(){
        this.checked = false;
      });
    }
  });

  $('input', $filter).change(function(){
    searchDelayed();
  });
});
