// Functions used by login pages

function cookiesEnabled() {
  // Test whether cookies are enabled by attempting to set a cookie and then change its value
  // set test cookie
  var c = "cookieTest=0";
  document.cookie = c;
  var dc = document.cookie;
  // cookie not set?  fail
  if (dc.indexOf(c) == -1) return 0;
  // change test cookie
  c = "cookieTest=1";
  document.cookie = c;
  dc = document.cookie;
  // cookie not changed?  fail
  if (dc.indexOf(c) == -1) return 0;
  // delete cookie
  // document.cookie = "cookieTest=; expires=Thu, 01-Jan-70 00:00:01 GMT";
  return 1;
}

function setLoginVars(user_name_id, alt_user_name_id, password_id, empty_password_id, js_enabled_id, cookies_enabled_id) {
  // Indicate that javascript is enabled, set cookie status, copy username and password length info to 
  // alternative variables since these vars are removed from the request by zope's authentication mechanism.
  if (js_enabled_id) {
    document.getElementById(js_enabled_id).value = 1;
  }
  if (cookies_enabled_id) {
    document.getElementById(cookies_enabled_id).value = cookiesEnabled();
  }
  if (user_name_id && alt_user_name_id) {
    user_name = document.getElementById(user_name_id)
    alt_user_name = document.getElementById(alt_user_name_id)
    if (user_name && alt_user_name) {
       alt_user_name.value = user_name.value;
    } 
  }
  if (password_id && empty_password_id) {
    password = document.getElementById(password_id)
    empty_password = document.getElementById(empty_password_id)
    if (password && empty_password) {
       if (password.value.length==0) {
          empty_password.value = '1';
       } else {
          empty_password.value = '0';
       }
    }
  }
  return 1;
}

function showEnableCookiesMessage() {
  // Show the element with id enable_cookes_message if cookies are not enabled
  if (!cookiesEnabled()) {
    msg = document.getElementById('enable_cookies_message')
    if (msg) {
       msg.style.display = 'block';
    }
  }
}
// Call showEnableCookiesMessage after the page loads
registerPloneFunction(showEnableCookiesMessage);
