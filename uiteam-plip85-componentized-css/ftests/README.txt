Required Packages

    - Mechanize: http://wwwsearch.sourceforge.net/mechanize/

        Browser class simulates major browser commands.  Provides stateful access
            to a web page.
        
    - ClientForm: http://wwwsearch.sourceforge.net/ClientForm/

        Package that lets you inspect, populate, and submit forms.
        
    - ClientCookie: http://wwwsearch.sourceforge.net/ClientCookie/

        Package that lets you simulate a browser that accepts and persists cookies.
        
    - pullparser: http://wwwsearch.sourceforge.net/pullparser/

        Package that enables simplified parsing of html documents.
        
    

Mechanize API

    Most functional tests will make heavy use of the mechanize API.  Here it is,
    taken from the mechanize package source code.

    Browser-like functions

        open(url, data=None)

            Open a web page with a specified url and returns a response object.  
            The data argument lets you post arguments by hand and should be
            of the form returned by urllib.urlencode, e.g.
            open('http://www.plone.org', data=urllib.urlencode({'__ac_name':'beavis'

        close()

            Close page(?).  I think the response object is still usable after
            being closed.

        reload()

            Reload current document, and return response object.

        back()

            Go back one step in history, and return response object.

        click(*args, **kwds):

            Return request that would result from clicking on a control.
    
            The request object is a urllib2.Request instance, which you can pass to
            urllib2.urlopen (or ClientCookie.urlopen).
    
            Only some control types (INPUT/SUBMIT & BUTTON/SUBMIT buttons and
            IMAGEs) can be clicked.
    
            Will click on the first clickable control, subject to the name, type
            and nr arguments (as for find_control).  If no name, type, id or number
            is specified and there are no clickable controls, a request will be
            returned for the form in its current, un-clicked, state.
    
            IndexError is raised if any of name, type, id or nr is specified but no
            matching control is found.  ValueError is raised if the HTMLForm has an
            enctype attribute that is not recognised.
    
            You can optionally specify a coordinate to click at, which only makes a
            difference if you clicked on an image.

        submit(*args, **kwds)

            Submit current form.

            Arguments are as for click() above.


        click_link(link=None, **kwds)

            Find a link and return a Request object for it.
    
            Arguments are as for .find_link() below, except that a link may be supplied
            as the first argument.

        follow_link(self, link=None, **kwds)

            Find a link and .open() it.
    
            Arguments are as for .click_link().


    Access to page features
    
        geturl() 

            Returns the URL of the current page.

        links(self, *args, **kwds)

            Returns a list of links on the current page

        forms()

            Returns a list of forms on the current page.

        viewing_html()

            See if we are currently viewing an HTML page.  Returns 0 or 1.

        title()

            Return document title, or None if there is no title element in the document

        select_form(name=None, predicate=None, nr=None)

            Select an HTML form for input.

            This is like giving a form the "input focus" in a browser.
    
            If a form is selected, the object supports the HTMLForm interface, so
            you can call methods like .set_value(), .set(), and .click().
    
            At least one of the name, predicate and nr arguments must be supplied.
            If no matching form is found, mechanize.FormNotFoundError is raised.
    
            If name is specified, then the form must have the indicated name.
    
            If predicate is specified, then the form must match that function.  The
            predicate function is passed the HTMLForm as its single argument, and
            should return a boolean value indicating whether the form matched.
    
            nr, if supplied, is the sequence number of the form (where 0 is the
            first).  Note that control 0 is the first form matching all the other
            arguments (if supplied); it is not necessarily the first control in the
            form.

        find_link(*args, **kwds)
        
            Find a link in current page.
    
            Links are returned as mechanize.Link objects.
    
            # Return third link that .search()-matches the regexp "python"
            # (by ".search()-matches", I mean that the regular expression method
            # .search() is used, rather than .match()).
            find_link(text_regex=re.compile("python"), nr=2)
    
            # Return first http link in the current page that points to somewhere
            # on python.org whose link text (after tags have been removed) is
            # exactly "monty python" have been removed).
            find_link(text="monty python",
                      url_regex=re.compile("http.*python.org"))
    
            # Return first link with exactly three HTML attributes.
            find_link(predicate=lambda link: len(link.attrs) == 3)
    
            Links include anchors (<a>), image maps (<area>), and frames (<frame>,
            <iframe>).
    
            All arguments must be passed by keyword, not position.  Zero or more
            arguments may be supplied.  In order to find a link, all arguments
            supplied must match.
    
            If a matching link is not found, mechanize.LinkNotFoundError is raised.
    
            text: link text between link tags: eg. <a href="blah">this bit</a> (as
             returned by pullparser.get_compressed_text(), ie. without tags but
             with opening tags "textified" as per the pullparser docs) must compare
             equal to this argument, if supplied
            text_regex: link text between tag (as defined above) must match the
             regular expression object passed as this argument, if supplied
            name, name_regex: as for text and text_regex, but matched against the
             name HTML attribute of the link tag
            url, url_regex: as for text and text_regex, but matched against the
             URL of the link tag (note this matches against Link.url, which is a
             relative or absolute URL according to how it was written in the HTML)
            tag: element name of opening tag, eg. "a"
            predicate: a function taking a Link object as its single argument,
             returning a boolean result, indicating whether the links
            nr: matches the nth link that matches all other criteria (default 0)


HTMLForm API

    When you select a form using mechanize.select_form(), you can then use
    the HTMLForm API on the browser.  Here it is, courtesy of the ClientForm
    package source.


    Represents a single HTML <form> ... </form> element.

    A form consists of a sequence of controls that usually have names, and
    which can take on various values.  The values of the various types of
    controls represent variously: text, zero-or-one-of-many or many-of-many
    choices, and files to be uploaded.  Some controls can be clicked on to
    submit the form, and clickable controls' values sometimes include the
    coordinates of the click.

    Forms can be filled in with data to be returned to the server, and then
    submitted, using the click method to generate a request object suitable for
    passing to urllib2.urlopen (or the click_request_data or click_pairs
    methods if you're not using urllib2).

    import ClientForm
    forms = ClientForm.ParseFile(html, base_uri)
    form = forms[0]

    form["query"] = "Python"
    form.set("lots", "nr_results")

    response = urllib2.urlopen(form.click())

    Usually, HTMLForm instances are not created directly.  Instead, the
    ParseFile or ParseResponse factory functions are used.  If you do construct
    HTMLForm objects yourself, however, note that an HTMLForm instance is only
    properly initialised after the fixup method has been called (ParseFile and
    ParseResponse do this for you).  See ListControl.__doc__ for the reason
    this is required.

    Indexing a form (form["control_name"]) returns the named Control's value
    attribute.  Assignment to a form index (form["control_name"] = something)
    is equivalent to assignment to the named Control's value attribute.  If you
    need to be more specific than just supplying the control's name, use the
    set_value and get_value methods.

    ListControl values are lists of item names.  The list item's name is the
    value of the corresponding HTML element's "value" attribute.

    Example:

      <INPUT type="CHECKBOX" name="cheeses" value="leicester"></INPUT>
      <INPUT type="CHECKBOX" name="cheeses" value="cheddar"></INPUT>

    defines a CHECKBOX control with name "cheeses" which has two items, named
    "leicester" and "cheddar".

    Another example:

      <SELECT name="more_cheeses">
        <OPTION>1</OPTION>
        <OPTION value="2" label="CHEDDAR">cheddar</OPTION>
      </SELECT>

    defines a SELECT control with name "more_cheeses" which has two items,
    named "1" and "2" (because the OPTION element's value HTML attribute
    defaults to the element contents).

    To set, clear or toggle individual list items, use the set and toggle
    methods.  To set the whole value, do as for any other control:use indexing
    or the set_/get_value methods.

    Example:

    # select *only* the item named "cheddar"
    form["cheeses"] = ["cheddar"]
    # select "cheddar", leave other items unaffected
    form.set("cheddar", "cheeses")

    Some controls (RADIO and SELECT without the multiple attribute) can only
    have zero or one items selected at a time.  Some controls (CHECKBOX and
    SELECT with the multiple attribute) can have multiple items selected at a
    time.  To set the whole value of a ListControl, assign a sequence to a form
    index:

    form["cheeses"] = ["cheddar", "leicester"]

    If the ListControl is not multiple-selection, the assigned list must be of
    length one.

    To check whether a control has an item, or whether an item is selected,
    respectively:

    "cheddar" in form.possible_items("cheeses")
    "cheddar" in form["cheeses"]  # (or "cheddar" in form.get_value("cheeses"))

    Note that some list items may be disabled (see below).

    Note the following mistake:

    form[control_name] = control_value
    assert form[control_name] == control_value  # not necessarily true

    The reason for this is that form[control_name] always gives the list items
    in the order they were listed in the HTML.

    List items (hence list values, too) can be referred to in terms of list
    item labels rather than list item names.  Currently, this is only possible
    for SELECT controls (this is a bug).  To use this feature, use the by_label
    arguments to the various HTMLForm methods.  Note that it is *item* names
    (hence ListControl values also), not *control* names, that can be referred
    to by label.

    The question of default values of OPTION contents, labels and values is
    somewhat complicated: see SelectControl.__doc__ and
    ListControl.get_item_attrs.__doc__ if you think you need to know.

    Controls can be disabled or readonly.  In either case, the control's value
    cannot be changed until you clear those flags (see example below).
    Disabled is the state typically represented by browsers by `greying out' a
    control.  Disabled controls are not `successful' -- they don't cause data
    to get returned to the server.  Readonly controls usually appear in
    browsers as read-only text boxes.  Readonly controls are successful.  List
    items can also be disabled.  Attempts to select disabled items (with
    form[name] = value, or using the ListControl.set method, for example) fail.
    Attempts to clear disabled items are allowed.

    If a lot of controls are readonly, it can be useful to do this:

    form.set_all_readonly(False)

    When you want to do several things with a single control, or want to do
    less common things, like changing which controls and items are disabled,
    you can get at a particular control:

    control = form.find_control("cheeses")
    control.disabled = False
    control.readonly = False
    control.set_item_disabled(False, "gruyere")
    control.set("gruyere")

    Most methods on HTMLForm just delegate to the contained controls, so see
    the docstrings of the various Control classes for further documentation.
    Most of these delegating methods take name, type, kind, id and nr arguments
    to specify the control to be operated on: see
    HTMLForm.find_control.__doc__.

    ControlNotFoundError (subclass of ValueError) is raised if the specified
    control can't be found.  This includes occasions where a non-ListControl
    is found, but the method (set, for example) requires a ListControl.
    ItemNotFoundError (subclass of ValueError) is raised if a list item can't
    be found.  ItemCountError (subclass of ValueError) is raised if an attempt
    is made to select more than one item and the control doesn't allow that, or
    set/get_single are called and the control contains more than one item.
    AttributeError is raised if a control or item is readonly or disabled and
    an attempt is made to alter its value.

    XXX CheckBoxControl and RadioControl don't yet support item access by label

    Security note: Remember that any passwords you store in HTMLForm instances
    will be saved to disk in the clear if you pickle them (directly or
    indirectly).  The simplest solution to this is to avoid pickling HTMLForm
    objects.  You could also pickle before filling in any password, or just set
    the password to "" before pickling.


    Public attributes:

    action: full (absolute URI) form action
    method: "GET" or "POST"
    enctype: form transfer encoding MIME type
    name: name of form (None if no name was specified)
    attrs: dictionary mapping original HTML form attributes to their values

    controls: list of Control instances; do not alter this list
     (instead, call form.new_control to make a Control and add it to the
     form, or control.add_to_form if you already have a Control instance)



    Methods for form filling:
    -------------------------

    Most of the these methods have very similar arguments.  See
    HTMLForm.find_control.__doc__ for details of the name, type, kind and nr
    arguments.  See above for a description of by_label.

    def find_control(self,
                     name=None, type=None, kind=None, id=None, predicate=None,
                     nr=None)

    get_value(name=None, type=None, kind=None, id=None, nr=None,
              by_label=False)
    set_value(value,
              name=None, type=None, kind=None, id=None, nr=None,
              by_label=False)

    set_all_readonly(readonly)


    Methods applying only to ListControls:

    possible_items(name=None, type=None, kind=None, id=None, nr=None,
                   by_label=False)

    set(selected, item_name,
        name=None, type=None, kind=None, id=None, nr=None,
        by_label=False)
    toggle(item_name,
           name=None, type=None, id=None, nr=None,
           by_label=False)

    set_single(selected,
               name=None, type=None, kind=None, id=None, nr=None,
               by_label=False)
    toggle_single(name=None, type=None, kind=None, id=None, nr=None,
                  by_label=False)


    Method applying only to FileControls:

    add_file(file_object,
             content_type="application/octet-stream", filename=None,
             name=None, id=None, nr=None)


    Methods applying only to clickable controls:

    click(name=None, type=None, id=None, nr=0, coord=(1,1))
    click_request_data(name=None, type=None, id=None, nr=0, coord=(1,1))
    click_pairs(name=None, type=None, id=None, nr=0, coord=(1,1))

