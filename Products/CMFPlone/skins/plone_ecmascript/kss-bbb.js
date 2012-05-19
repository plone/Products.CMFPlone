(function($){

/* Calendar Portlet KSS Replacement */
$('#calendar-next,#calendar-previous').live('click', function(){
    $('#kss-spinner').show();
    var el = $(this);
    var container = el.parents('.portletWrapper');
    var id = container.attr('id');
    var hash = id.substring("portletwrapper-".length, id.length);
    $.ajax({
        url: $('base').attr('href') + '/@@render-portlet',
        data: {
            portlethash: hash,
            month: el.data('month'),
            year: el.data('year')
        },
        success: function(data){
            container.html(data);
            $('#kss-spinner').hide();
        },
        error: function(){
            $('#kss-spinner').hide();
        }
    });
    return false;
});


})(jQuery);
