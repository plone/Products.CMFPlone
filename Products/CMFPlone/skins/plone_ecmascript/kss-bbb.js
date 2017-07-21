(function($){

/**
* Polyfill to add data attributes as fallback if main_template.pt is customized
*/
$(document).ready(function(){
    if (typeof($('body').attr('data-portal-url')) !== 'undefined' &&
        typeof($('body').attr('data-base-url')) !== 'undefined') {
        return;
    }
    $('body').attr('data-portal-url', portal_url);

    // Try to guess context url
    //
    // using this method we keep the get parameters used with plone protect     
    // https://gist.github.com/jlong/2428561
    var parser = document.createElement('a');       
    parser.href = location.href;

    // Remove views that we know Plone has from the URL
    var knownViews = [
        /\/folder_contents/,  // Plone folder_contents view
        /\/edit/,             // Plone edit page
        /\/@@.*/              // All other browser views
    ];
    knownViews.forEach(function(viewRegex){
        parser.pathname = parser.pathname.replace(viewRegex, '');
    });

    $('body').attr('data-base-url', parser.href);
});

function refreshPortlet(hash, _options){
    var options = {
        data: {},
        success: function(){},
        error: function(){},
        ajaxOptions: {}};
    $.extend(options, _options);
    options.data.portlethash = hash;
    ajaxOptions = options.ajaxOptions;
    ajaxOptions.url = $('body').attr('data-base-url') + '/@@render-portlet';
    ajaxOptions.success = function(data){
        var container = $('[data-portlethash="' + hash + '"]');
        var portlet = $(data);
        container.html(portlet);
        options.success(data, portlet);
    }
    ajaxOptions.error = function(){
        options.error();
    }
    ajaxOptions.data = options.data;
    $.ajax(ajaxOptions);
}


/* apply a refresh timeout to a portlet */
function applyPortletTimeout(portlet){
    var timeout = portlet.data('timeout');
    if(timeout == undefined){
        timeout = 30; // Default to 30 seconds
    }else{
        timeout = parseInt(timeout);
    }
    timeout = timeout * 1000;
    setTimeout($.proxy(function(){
        refreshPortlet(this.parents('.portletWrapper').data('portlethash'), {
            success: function(data, portlet){
                apply_timeout(portlet);
            }
        });
    }, portlet), timeout);
}


/* dom loaded related actions */
$(document).ready(function(){
    /* Show animated spinner while AJAX is loading. */
    var spinner = $('<div id="ajax-spinner"><img src="' + portal_url + '/spinner.gif" alt=""/></div>');
    spinner.appendTo('body').hide();
    $(document).ajaxStart(function() { spinner.show(); });
    $(document).ajaxStop(function() { spinner.hide(); });

    /* Calendar Portlet KSS Replacement */
    $('body').delegate('#calendar-next,#calendar-previous', 'click', function(e){
        e.preventDefault();
        var el = $(this);
        var container = el.parents('.portletWrapper');
        refreshPortlet(container.data('portlethash'), {
            data: {
                month: el.data('month'),
                year: el.data('year')
            }
        });
        return false;
    });

    /* Any portlets with the class kssPortletRefresh(deprecated)
       or refreshPortlet will automatically be refreshed with this.
       Data attribute timeout(data-timeout) will be used to override
       the timeout used for the refresh */
    $('.kssPortletRefresh,.refreshPortlet').each(function(){
        applyPortletTimeout($(this));
    });

    /* deferred rendering portlets */
    $('.portlet-deferred').each(function(){
        refreshPortlet($(this).parents('.portletWrapper').data('portlethash'));
    });

    /* sharing related kss */
    function updateSharing(data){
        var sharing = data.body;
        var messages = $(data.messages).filter(function(){ return this.tagName == 'DL'; });
        $('.portalMessage').remove();
        $('#user-group-sharing').replaceWith(sharing);
        $('#content').prepend(messages);
    }

    /* sharing search form */
    var search_timeout = null;
    $('#content-core').delegate('#sharing-user-group-search', 'input', function(){
        var text = $(this);
        if(search_timeout != null){
            clearTimeout(search_timeout);
        }
        if(text.val().length > 3){
            search_timeout = setTimeout($.proxy(function(){
                $('#sharing-search-button').trigger('click');
            }, text), 300);
        }
    });

    $('#content-core').delegate('#sharing-search-button', 'click', function(){
        $.ajax({
            url: $('body').attr('data-base-url') + '/@@updateSharingInfo',
            data: {
                search_term: $('#sharing-user-group-search').val(),
                'form.button.Search': 'Search'
            },
            type: 'GET',
            dataType: 'json',
            success: updateSharing
        });
        return false;
    });

    /* Sharing save button */
    $('#content-core').delegate('#sharing-save-button', 'click', function(){
        var btn = $(this);
        var form = btn.parents('form');
        var data = form.serializeArray();
        data.push({name: 'form.button.Save', value: 'Save'});
        $.ajax({
            url: $('body').attr('data-base-url') + '/@@updateSharingInfo',
            data: data,
            type: 'POST',
            dataType: 'json',
            success: updateSharing
        });
        return false;
    });

});

})(jQuery);
