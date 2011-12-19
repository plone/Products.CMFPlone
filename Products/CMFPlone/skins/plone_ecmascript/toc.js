/* Creates table of contents for pages for h[1234] */

jQuery(function($) {
    var dest, content, location, stack, oltoc, numdigits, wlh, target,
        targetOffset;
    
    dest = $('dl.toc dd.portletItem');
    content = $('#region-content,#content');
    if (!content || !dest.length) {return;}
    
    dest.empty();

    location = window.location.href;
    if (window.location.hash) {
        location = location.substring(0, location.lastIndexOf(window.location.hash));
    }
    stack = [];
    // Get headers in document order
    $(content).find('*').not('.comment > h3').filter(function() { return (/^h[1234]$/).test(this.tagName.toLowerCase()); })
        .not('.documentFirstHeading').each(function(i) {
        var level, ol, li;

        level = this.nodeName.charAt(1);
        // size the stack to the current level
        while (stack.length < level) {
            ol = $('<ol>');
            if (stack.length) {
                li = $(stack[stack.length - 1]).children('li:last');
                if (!li.length) {
                    // create a blank li for cases where, e.g., we have a subheading before any headings
                    li = $('<li>').appendTo($(stack[stack.length - 1]));
                }
                li.append(ol);
            }
            stack.push(ol);
        }
        while (stack.length > level) {stack.pop();}
        
        $(this).before($('<a name="section-' + i + '" />'));
        $('<li>').append(
            $('<a />').attr('href', location + '#section-' + i)
                    .text($(this).text()))
            .appendTo($(stack[stack.length - 1]));
    });

    if (stack.length) {
        var oltoc = $(stack[0]);
        // first level is a level with at least two entries #11160
        var i = 1;
        while(oltoc.children('li').length == 1){
            oltoc = $(stack[i]);
            i += 1;
        }
        
        if (i <= stack.length) {
            $('dl.toc').show();
        }
        
        numdigits = oltoc.children().length.toString().length;
        //Use a clever class name to add margin that's MUCH easier to customize
        oltoc.addClass("TOC"+numdigits+"Digit");
        dest.append(oltoc);

        //scroll to element now.
        wlh = window.location.hash;
        if (wlh) {
            target = $(wlh);
            target = target.length && target
                || $('[name=' + wlh.slice(1) +']');
            targetOffset = target.offset();
            if (targetOffset) {
                $('html,body').animate({scrollTop: targetOffset.top}, 0);
            }
        }
    }
});
