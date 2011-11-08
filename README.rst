 Robot-Framework Example Buildout:
 
 https://github.com/plone/buildout.coredev/tree/4.1-robot
 
 How to get started with Robot Framework:
 
 Fork the 4.1-robot repository:
 

    Go to https://github.com/plone/buildout.coredev/tree/4.1-robot

    Click the "Fork" Button

    A new fork will be available at https://github.com/<YOUR_GITHUB_USERNAME>/buildout.coredev/

   
 Clone and create the Robot Framework coredev buildout:
 
   $ git clone https://github.com/<YOUR_GITHUB_USERNAME>/buildout.coredev
   $ cd buildout.coredev
   $ git checkout 4.1-robot
   
   or use
   $ git clone -b 4.1-robot https://github.com/<YOUR_GITHUB_USERNAME/buildout.coredev
   to clone the branch
   
   $ python2.6 bootstrap.py
   $ bin/buildout -c pybot.cfg
Once buildout is completed, to run the sample tests type
 $ bin/pybot acceptance-tests
 
 If you want pybot to leave the browser up at the point of a failure so you can inspect the fialure, you can use the following:
 
 $ bin/pybot --runmode SkipTeardownOnExit --runmode ExitOnFailure acceptance-tests
  
 
 If you get any of the following errors try these solutions
 
 Error: Error: Couldn't find a distribution for 'robotframework-seleniumlibrary'.
 
 Solution: Make sure you have Mercurial installed on your system.
 
 Error: [ ERROR ] Parsing '/home/emanlove/buildout.coredev/acceptance-tests' failed: Data source does not exist.
Solution: You need to re-fetch the repository and merge with your local repository. Try
$ git fetch plone
$ git merge plone/4.1-plone
 
