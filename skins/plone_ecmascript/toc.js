$(function() {
    var dest = $('dl.toc dd.portletItem');
    var content = getContentArea();
    if (!content || !dest.length) return;
    
    dest.empty();

    var location = window.location.href;
    if (window.location.hash)
        location = location.substring(0, location.lastIndexOf(window.location.hash));

    var stack = [];
    // Get headers in document order
    $(content).find('*').filter(function() { return /^h[1234]$/.test(this.tagName.toLowerCase()) })
              .not('.documentFirstHeading').each(function(i) {
        var level = this.nodeName[1];
        // size the stack to the current level
        while (stack.length < level) {
            var ol = $('<ol>');
            if (stack.length) $(stack[stack.length - 1]).append(ol);
            stack.push(ol);
        }
        while (stack.length > level) stack.pop();
        
        $(this).before($('<a>').attr('name', 'section-' + i));

        $('<li>').append(
            $('<a>').text($(this).text())
                    .attr('href', location + '#section-' + i))
            .appendTo($(stack[stack.length - 1]));
    });

    if (stack.length) {
        $('dl.toc').show();
        dest.append(stack[0]);
    }
});
