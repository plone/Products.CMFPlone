function siteid_focus() {
  "use strict";
  var siteid = document.getElementById('site_id');
  siteid.focus();
}

function set_timezone() {
  "use strict";
  var i, tzopt,
      tz = jstz.determine(),
      tzname = tz.name(),
      tzopts = document.getElementById('portal_timezone').options;
  for (i=1; i<=tzopts.length; i++) {
    tzopt = tzopts[i-1];
    if (tzname === tzopt.value){
      tzopt.selected = 'selected';
      break;
    }
  }
}
window.onload = function () {
  "use strict";
  siteid_focus();
  set_timezone();
};
