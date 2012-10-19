(function($){
$(document).ready(function(){
    $('#portal-columns').delegate('.portlet-action', 'submit', function(e){
        $('#kss-spinner').show();
        var form = $(this);
        var formdata = form.serializeArray();
        var data = {};
        for(var i=0; i<formdata.length; i++){
            data[formdata[i].name] = formdata[i].value;
        }
        data.ajax = true;
        $.ajax({
            url: form.attr('action'),
            data: data,
            type: 'POST',
            success: function(data){
                var container = form.parents('.portlets-manager');
                container.replaceWith($(data));
                $('#kss-spinner').hide();
            },
            error: function(){
                $('#kss-spinner').hide();
            }
        });
        return false;
    });
});
})(jQuery);