CMFPlone tests depend on the ZopeTestCase package.

As of this writing ZopeTestCase is hosted in the Collective CVS. It comes
with useful documentation worth reading. <wink>

The required version of ZopeTestCase is 0.9.0 or better.

Note that ZopeTestCase must be installed into lib/python/Testing and *not*
lib/python/Products!

The ZopeTestCase homepage is here:
http://zope.org/Members/shh/ZopeTestCase


How to run the tests:

  Setup your enviroment variables and run the test modules:

    - Set SOFTWARE_HOME to point to your Zope installation, e.g: /usr/lib/zope/lib/python

    - If you use a zope instance setup set INSTANCE_HOME to your Zope instance, e.g: /var/lib/zope/instance/default

    - Run single test: python testInterfaceTool.py

    - Run test-suite: python runalltests.py

  Alternatively you may use the testrunner utility:

    - Install the INSTANCE_HOME-aware testrunner.py from http://www.zope.org/Members/shh/TestRunner

    - Run single test: python /path/to/zope/utilites/testrunner.py -qif testMyCoolProduct.py

    - Run all tests: python /path/to/zope/utilites/testrunner.py -qia

    - If this fails, you probably link your products into your instance, so use: 
      python /path/to/zope/utilites/testrunner.py -qa -I /path/to/your/instance


How to setup a new unittest for a CMFPlone component:

    - Install ZopeTestCase                                                                                      
                                                                                                                
    - Install testrunner.py                                                                                     
                                                                                                                
    - Copy one of the testSkeleton* files and give it a new name, starting with 'test', e.g: testMyCoolProduct.py
                                                                                                                
    - Open the new script and change all instances of 'SomeProduct' to the name of your product.                
                                                                                                                

How to use ZopeTestCase with a Plone/CMF based Product:   

    - Install Plone                                                           

    - Install ZopeTestCase                                                                                      
                                                                                                                
    - Install testrunner.py                                                                                     
                                                                                                                
    - In your Products directory create a directory named 'tests'                                                
                                                                                                                
    - Copy the following files from CMFPlone/tests into 'tests': 
    
        - framework.py

        - runalltests.py   
                                                                                                                                                                                                                             
    - Copy one of the testSkeleton* files and give it a new name, starting with 'test', e.g: testMyCoolProduct.py
                                                                                                                
    - Open the new script and change all instances of 'SomeProduct' to the name of your product.    

