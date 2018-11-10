Browser and webdriver support
-----------------------------

2017-07-20:

Ubuntu 16.04:

- Phantomjs works well, but has issues with iframes. The `working_with_tinymce.robot` tests have visual errors in the screenshots.
- Chrome 59 with chromedriver has issues, reportedly Chrome 60 should be better, and be able to do headless screenshots.
- Firefox 54 does not work with the current geckodriver software for Linux.
