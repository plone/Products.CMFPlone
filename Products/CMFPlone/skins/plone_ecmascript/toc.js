(function($) { $(function() {
    var dest = $('dl.toc dd.portletItem');
    var content = getContentArea();
    if (!content || !dest.length) return;
    
    dest.empty();

    var location = window.location.href;
    if (window.location.hash)
        location = location.substring(0, location.lastIndexOf(window.location.hash));

    var stack = [];
    // Get headers in document order
    $(content).find('*').not('.comment > h3').filter(function() { return /^h[1234]$/.test(this.tagName.toLowerCase()) })
        .not('.documentFirstHeading').each(function(i) {
        var level = this.nodeName.charAt(1);
        // size the stack to the current level
        while (stack.length < level) {
            var ol = $('<ol>');
            if (stack.length) {
                var li = $(stack[stack.length - 1]).children('li:last');
                if (!li.length)
                    // create a blank li for cases where, e.g., we have a subheading before any headings
                    li = $('<li>').appendTo($(stack[stack.length - 1]));
                li.append(ol);
            }
            stack.push(ol);
        }
        while (stack.length > level) stack.pop();
        
        $(this).before($('<a name="section-' + i + '" />'));
        $('<li>').append(
            $('<a />').attr('href', location + '#section-' + i)
                    .text($(this).text()))
            .appendTo($(stack[stack.length - 1]));
    });

    if (stack.length) {
        $('dl.toc').show();
        var oltoc = $(stack[0]);
        // first level is a level with at least two entries #11160
        var i = 1;
        while(oltoc.children('li').length == 1){
            oltoc = $(stack[i]);
            i += 1;
        }
        numdigits = oltoc.children().length.toString().length;
        //Use a clever class name to add margin that's MUCH easier to customize
        oltoc.addClass("TOC"+numdigits+"Digit");
        dest.append(oltoc);

        //scroll to element now.
        var wlh = window.location.hash;
        if (wlh) {
            var target = $(wlh);
            target = target.length && target
                || $('[name=' + wlh.slice(1) +']');
            var targetOffset = target.offset();
            if (targetOffset)
                $('html,body').animate({scrollTop: targetOffset.top}, 0);
        }
    }
}); })(jQuery);
