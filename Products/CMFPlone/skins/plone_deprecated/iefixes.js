/* Special fixes for Internet Explorer */


/* this stops IE6 from caching background images */
try
{
    document.execCommand("BackgroundImageCache", false, true)
}
catch(err)
{
    //do nothing
}
