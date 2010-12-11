
/********* Table sorter script *************/
/*
 * For all table elements with 'listing' class,
 * when user clicks on a th without 'nosort' class,
 * it sort table values using the td class with 'sortabledata-mydata' name,
 * or the td text content
 *
 */
(function($) {

function sortabledataclass(cell){
	var re = new RegExp("sortabledata-([^ ]*)","g");
	var matches = re.exec(cell.attr('class'));
	if(matches) return matches[1]
	else return null
}

function sortable(cell) {
    // convert a cell a to something sortable

	// use sortabledata-xxx cell class if it is defined
	var text = sortabledataclass(cell);
	if(text == null) text = cell.text();

	// A number, but not a date?
    if (text.charAt(4) != '-' && text.charAt(7) != '-' && !isNaN(parseFloat(text)))
        return parseFloat(text);
    return text.toLowerCase();
}

function sort() {
	var th = $(this).closest('th');
	var colnum = $('th', $(this).closest('thead')).index(th);
    var table = $(this).parents('table:first');
    var tbody = table.find('tbody:first');
    var reverse = table.attr('sorted') == colnum;

    $(this).parent().find('th:not(.nosort) .sortdirection')
        .html('&#x2003;');
    $(this).children('.sortdirection').html(
        reverse ? '&#x25b2;' : '&#x25bc;');

    var index = $(this).parent().children('th').index(this);
    var data = [];
    var usenumbers = true;
    tbody.find('tr').each(function() {
        var cells = $(this).children('td');
        var sortableitem = sortable(cells.slice(index,index+1));
        if (isNaN(sortableitem)) usenumbers = false;
        data.push([
            sortableitem,
            // crude way to sort by surname and name after first choice
            sortable(cells.slice(1,2)), sortable(cells.slice(0,1)),
            this]);
    });

    if (data.length) {
        if (usenumbers)
            data.sort(function(a,b) {return a[0]-b[0];});
        else
            data.sort();
        if (reverse) data.reverse();
        table.attr('sorted', reverse ? '' : colnum);

        // appending the tr nodes in sorted order will remove them from their old ordering
        tbody.append($.map(data, function(a) { return a[3]; }));
        // jquery :odd and :even are 0 based
        tbody.each(setoddeven);
    }
}

function setoddeven() {
    var tbody = $(this);
    // jquery :odd and :even are 0 based
    tbody.find('tr').removeClass('odd').removeClass('even')
        .filter(':odd').addClass('even').end()
        .filter(':even').addClass('odd');
}

$(function() {
    // set up blank spaceholder gif
    var blankarrow = $('<span>&#x2003;</span>').addClass('sortdirection');
    // all listing tables not explicitly nosort, all sortable th cells
    // give them a pointer cursor and  blank cell and click event handler
    // the first one of the cells gets a up arrow instead.
    $('table.listing:not(.nosort) thead th:not(.nosort)')
        .append(blankarrow.clone())
        .css('cursor', 'pointer')
        .click(sort);
    $('table.listing:not(.nosort) tbody').each(setoddeven);
});

})(jQuery);
