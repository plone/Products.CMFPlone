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
  if($loader.length === 0){
    $loader = $('<div class="plone-loader"><div class="spinner-border text-secondary" role="status"></div></div>');
    $('body').append($loader);
  }

  var $filter = $('#search-filter');
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

  var setBatchStart = function(b_start){
    $("#search-batch-start").attr("value", b_start);
  };

  // for sorme reason the backend always flag with active class the sorting options
  var updateSortingState = function($el){
    $('a', $sortingContainer).removeClass('active');
    $el.addClass('active');
  };
  var default_sort = $('#search-results').attr('data-default-sort');
  updateSortingState($('a[data-sort='+default_sort+']'));

  /* sorting */
  $('a', $sortingContainer).click(function(e){
    e.preventDefault();
    updateSortingState($(this));
    var sort = $(this).attr('data-sort');
    var order = $(this).attr('data-order');
    if(sort){
      $('[name="sort_on"]').attr('value', sort);
      if(order && order == 'reverse'){
        $('[name="sort_order"]').attr('value', 'reverse');
      }else{
        $('[name="sort_order"]').attr('value', '');
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
    setBatchStart("0");
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
    setBatchStart("0");
    searchDelayed();
  });

  /* pagination */
  $("#searchform").on("click", ".pagination a", function(e) {
    var urlParams = new URLSearchParams($(e.currentTarget).attr("href")),
        b_start = urlParams.get("b_start:int");
    if(!b_start) {
      // not plone pagination
      return;
    }
    e.preventDefault();
    setBatchStart(b_start);
    search();
  })
});
