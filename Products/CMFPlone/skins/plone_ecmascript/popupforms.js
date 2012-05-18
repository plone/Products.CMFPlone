/******
    Set up standard Plone popups
    
    Provides globals: common_content_filter
    
    Extends jQuery.tools.overlay.conf to set up common Plone effects and
    visuals.
******/


var common_content_filter = '#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info';

jQuery.extend(jQuery.tools.overlay.conf, 
    {
        fixed:false,
        speed:'fast',
        mask:{color:'#fff',opacity: 0.4,loadSpeed:0,closeSpeed:0}
    });


(function($) {
		
	// static constructs
	$.plonepopups = $.plonepopups || {};
    
    $.extend($.plonepopups,
        {
            // method to show error message in a noform
            // situation.
            noformerrorshow: function noformerrorshow(el, noform) {
                var o = $(el),
                    emsg = o.find('dl.portalMessage.error');
                if (emsg.length) {
                    o.children().replaceWith(emsg);
                    return false;
                } else {
                    return noform;
                }
            },
            // After deletes we need to redirect to the target page.
            redirectbasehref: function redirectbasehref(el, responseText) {
                var mo = responseText.match(/<base href="(\S+?)"/i);
                if (mo.length === 2) {
                    return mo[1];
                }
                return location;
            }
        })
})(jQuery);

jQuery(function($){

    if (jQuery.browser.msie && parseInt(jQuery.browser.version, 10) < 7) {
        // it's not realistic to think we can deal with all the bugs
        // of IE 6 and lower. Fortunately, all this is just progressive
        // enhancement.
        return;
    }
    
    // login form
    $('#portal-personaltools a[href$="/login"], #portal-personaltools a[href$="/login_form"], .discussion a[href$="/login"], .discussion a[href$="/login_form"]').prepOverlay(
        {
            subtype: 'ajax',
            filter: common_content_filter,
            formselector: 'form#login_form',
            noform: function () {
                if (location.href.search(/pwreset_finish$/) >= 0) {
                    return 'redirect';
                } else {
                    return 'reload';
                }
            },
            redirect: function () {
                var href = location.href;
                if (href.search(/pwreset_finish$/) >= 0) {
                    return href.slice(0, href.length-14) + 'logged_in';
                } else {
                    return href;
                }
            }
        }
    );

    // contact form
    $('#siteaction-contact a').prepOverlay(
        {
            subtype: 'ajax',
            filter: common_content_filter,
            formselector: 'form[name="feedback_form"]',
            noform: function(el) {return $.plonepopups.noformerrorshow(el, 'close');}
        }
    );

    // comment form
    $('form[name=reply]').prepOverlay(
        {
            subtype: 'ajax',
            filter: common_content_filter,
            formselector: 'form:has(input[name="discussion_reply:method"])',
            noform: function(el) {return $.plonepopups.noformerrorshow(el, 'redirect');},
            redirect: $.plonepopups.redirectbasehref
        }
    );


    // display: select content item / change content item
    $('#contextSetDefaultPage, #folderChangeDefaultPage').prepOverlay(
        {
            subtype: 'ajax',
            filter: common_content_filter,
            formselector: 'form[name="default_page_form"]',
            noform: function(el) {return $.plonepopups.noformerrorshow(el, 'reload');},
            closeselector: '[name=form.button.Cancel]',
            width:'40%'
        }
    );

    // advanced state
    // This form needs additional JS and CSS for the calendar widget.
    // The AJAX form doesn't load it from the javascript_head_slot.
    // $('dl#plone-contentmenu-workflow a#advanced').prepOverlay(
    //     {
    //         subtype: 'ajax',
    //         filter: common_content_filter,
    //         formselector: 'form',
    //         noform: function(el) {return $.plonepopups.noformerrorshow(el, 'reload');},
    //         closeselector: '[name=form.button.Cancel]'
    //     }
    // );

    // Delete dialog
    $('dl#plone-contentmenu-actions a#delete').prepOverlay(
        {
            subtype: 'ajax',
            filter: common_content_filter,
            formselector: '#delete_confirmation',
            noform: function(el) {return $.plonepopups.noformerrorshow(el, 'redirect');},
            redirect: $.plonepopups.redirectbasehref,
            closeselector: '[name=form.button.Cancel]',
            width:'50%'
        }
    );

    // Rename dialog
    $('dl#plone-contentmenu-actions a#rename').prepOverlay(
        {
            subtype: 'ajax',
            filter: common_content_filter,
            closeselector: '[name=form.button.Cancel]',
            width:'40%'
        }
    );

    // registration
    $('#portal-personaltools a[href$="/@@register"]').prepOverlay(
        {
            subtype: 'ajax',
            filter: common_content_filter,
            formselector: 'form.kssattr-formname-register'
        }
    );

    // add new user, group
    $('form[name=users_add], form[name=groups_add]').prepOverlay(
        {
            subtype: 'ajax',
            filter: common_content_filter,
            formselector: 'form.kssattr-formname-new-user, form[name="groups"]',
            noform: function(el) {return $.plonepopups.noformerrorshow(el, 'redirect');},
            redirect: function () {return location.href;}
        }
    );

    // Content history popup
    $('#content-history a').prepOverlay({
       subtype: 'ajax', 
       filter: 'h2, #content-history',
       urlmatch: '@@historyview',
       urlreplace: '@@contenthistorypopup'
    });

});

