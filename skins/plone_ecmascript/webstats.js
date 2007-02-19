// you can replace this with your own code to support any webanalytics package
// what is happening here is basically to inject the script tag after into
// the head after loading the page so that it does load even if the 
// external JS file is not accessible right then (installAnalyticsPackage).
// Then an event handler is registered which actually calls the function
// when it's loaded.
//
// remember to enable webstats.js in portal_javascripts after changing it
// here

function invokeAnalyticsPackage() {
    _uacct = "myid";    // add your own Google Analytics URL here
    urchinTracker();
}

function installAnalyticsPackage() {
    head = document.getElementsByTagName("head")[0];
    scriptnode = document.createElement("script");
    scriptnode.src = "http://www.google-analytics.com/urchin.js";
    scriptnode.id ="analyticsScript"
    head.appendChild(scriptnode);
    registerEventListener(scriptnode,"load",invokeAnalyticsPackage)
}

registerPloneFunction(installAnalyticsPackage);
