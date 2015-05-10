/* Javascript code to assist managing AtD ignored phrases */ 

/* taken from the public domain, source unknown */
function AtD_SetCookie( name, value, expires)
{
   var today = new Date();
   today.setTime( today.getTime() );

   if ( expires ) 
   {
      expires = expires * 1000 * 60 * 60 * 24;
   }
   var expires_date = new Date( today.getTime() + (expires) );

   document.cookie = name + "=" + escape( value ) + ( ( expires ) ? ";expires=" + expires_date.toGMTString() : "" );
}
			
/* taken from the public domain, source unknown */
function AtD_GetCookie( check_name ) 
{
   var a_all_cookies = document.cookie.split( ';' );
   var a_temp_cookie = '';
   var cookie_name = '';
   var cookie_value = '';
   var b_cookie_found = false; // set boolean t/f default f

   for ( i = 0; i < a_all_cookies.length; i++ )
   {
      a_temp_cookie = a_all_cookies[i].split( '=' );
      cookie_name = a_temp_cookie[0].replace(/^\s+|\s+$/g, '');

      if ( cookie_name == check_name )
      {
         b_cookie_found = true;
         if ( a_temp_cookie.length > 1 )
	 {
            cookie_value = unescape( a_temp_cookie[1].replace(/^\s+|\s+$/g, '') );
	 }
         return cookie_value;
         break;
      }
      a_temp_cookie = null;
      cookie_name = '';
   }
   if ( !b_cookie_found )
   {
      return null;
   }
}

function AtD_SetIgnoredPhrases(phrases)
{
   var results = new Array();

   for (var i =0; i < phrases.length; i++)
   {
      results.push(escape(phrases[i]) + "=1");
   }

   AtD_SetCookie("atd_ignore", results.join("&"), 365 * 3);
}

function AtD_GetIgnoredPhrases()
{
   var rawString = AtD_GetCookie("atd_ignore");
   if (rawString == null)
   {
      return new Array();
   }

   var results   = new Array();
   var phrases   = rawString.split(/\&/g);
   for (var i = 0; i < phrases.length; i++)
   {
      results.push(unescape(phrases[i].substr(0, phrases[i].length - 2)));
   }  

   return results;
}

function AtD_UnignorePhrase(phrase)
{
   var phrases = AtD_GetIgnoredPhrases();
   var results = new Array();
   for (var i = 0; i < phrases.length; i++)
   {
      if (phrases[i] != phrase)
      {
         results.push(phrases[i]);
      }
   }
   AtD_SetIgnoredPhrases(results);
}

