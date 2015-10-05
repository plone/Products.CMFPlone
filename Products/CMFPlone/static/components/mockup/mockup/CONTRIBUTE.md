# Code conventions

It's still on the TODO list to write this down,
but for now make sure you keep jshint happy.

To run jshint on mockup code you have to type: ```make jshint```.


# Git workflow / branching model

It is important that you *NEVER* commit to master directly.
Even for the smallest and most trivial fix.
*ALWAYS* open a pull request and ask somebody else to merge your code.
*NEVER* merge it yourself.

If you don't get feedback on your pull request in a day please come to ```#plone-framework``` and ping ```@garbas``` or ```@vangheem``` about it.

The main goal of this process is not to boss developers around and make their lives harder,
but to bring greater stability to the development of mockup and to make releases smooth and predictable.


# Pull request checklist

Checklist of things that every person accepting pull request should follow
(or else @garbas will make you drink a Mongolian cocktail - I promise!).

 - The title and description of a pull request *MUST* be descriptive and need to reflect the changes in code.
   Please review, line by line, and comment if the code change was not mentioned in the description of the pull request.

 - Copy the title of the pull request to the current ticket tracking changes for release under development.
   (example: https://github.com/plone/mockup/issues/250)

 - The full test suite (which runs the tests on saucelabs against real browsers) will only be triggered for the master branch and the pull requests.
   It is important that the tests pass before you merge it.

   Please note that the Travis job sometimes hangs (for various reasons) and then you need to restart it.

   Due to some bugs in Travis regarding reporting of the status,
   be sure to always check on https://travis-ci.org/plone/mockup/pull_requests that the tests really have passed.

 - It is important to never lower code coverage.
   Check [coveralls](https://coveralls.io/r/plone/mockup) to see that coverage hasn't dropped.
   It should be reported automatically once the tests pass.
   
   Make sure that every new function (or bigger chunk of code) that is added to mockup is tested.

 - All commits need to be rebased on current master and squashed into one single commit.
   The commit's title (first line) and description (row 3 and below) should be identical to the pull request.

 - Once you've ensured that all the above is correct,
   go ahead and merge the pull request.
   Make sure you always use a polite tone and explain why this is needed by linking to this document.


# Changing this page

When changing this document,
note that it must be done in public with the possibility for others to comment or at least be aware of the changes.

Create a pull request with your proposed changes and describe the reasoning behind the changes.

