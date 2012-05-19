(function($){

function refreshPortlet(hash, _options){
    var options = {
        data: {},
        success: function(){},
        error: function(){},
        ajaxOptions: {}};
    $.extend(options, _options);
    options.data.portlethash = hash;
    ajaxOptions = options.ajaxOptions;
    ajaxOptions.url = $('base').attr('href') + '/@@render-portlet';
    ajaxOptions.success = function(data){
        var container = $('[data-portlethash="' + hash + '"]');
        var portlet = $(data);
        container.html(portlet);
        $('#kss-spinner').hide();
        options.success(data, portlet);
    }
    ajaxOptions.error = function(){
        $('#kss-spinner').hide();
        options.error();
    }
    ajaxOptions.data = options.data;
    $.ajax(ajaxOptions);
}

/* Calendar Portlet KSS Replacement */
$('#calendar-next,#calendar-previous').live('click', function(){
    $('#kss-spinner').show();
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
});


})(jQuery);
