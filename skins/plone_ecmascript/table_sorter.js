
/********* Table sorter script *************/

function sortable(a) {
    // convert a to something sortable
    // A number, but not a date?
    if (a.charAt(4) != '-' && a.charAt(7) != '-' && !isNaN(parseFloat(a)))
        return parseFloat(a);    
    return a.toLowerCase();
}

function sort() {
    var name = $(this).text();
    var table = $(this).parents('table:first');
    var tbody = table.find('tbody:first');
    var reverse = table.attr('sorted') == name;

    $(this).parent().find('th:not(.nosort) img.sortdirection')
        .attr('src', portal_url + '/arrowBlank.gif');
    $(this).children('img.sortdirection').attr('src', portal_url + 
        (reverse ? '/arrowDown.gif' : '/arrowUp.gif'));
    
    var index = $(this).parent().children('th').index(this);
    var data = [];
    tbody.find('tr').each(function() {
        var cells = $(this).children('td');
        data.push([
            sortable(cells.slice(index,index+1).text()),
            // crude way to sort by surname and name after first choice
            sortable(cells.slice(1,2).text()), sortable(cells.slice(0,1).text()),
            this]);
    });

    if (data.length) {
        data.sort();
        if (reverse) data.reverse();
        table.attr('sorted', reverse ? '' : name);

        // appending the tr nodes in sorted order will remove them from their old ordering
        tbody.append($.map(data, 'a[3]'));
        // jquery :odd and :even are 0 based
        tbody.find('tr').removeClass('odd').removeClass('even')
            .filter(':odd').addClass('even').end()
            .filter(':even').addClass('odd');
    }    
}

$(function() {
    // set up blank spaceholder gif
    var blankarrow = $('<img>')
        .attr('src', portal_url + '/arrowBlank.gif')
        .attr('width', 6).attr('height', 9).addClass('sortdirection');
    // all listing tables not explicitly nosort, all sortable th cells
    // give them a pointer cursor and  blank cell and click event handler
    // the first one of the cells gets a up arrow instead.
    $('table.listing:not(.nosort) thead th:not(.nosort)')
        .append(blankarrow.clone())
        .css('cursor', 'pointer')
        .click(sort)
        .slice(0, 1)
        .find('img.sortdirection').attr('src', portal_url + '/arrowUp.gif');
});
