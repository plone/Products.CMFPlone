
CMFPlone tests depend on the ZopeTestCase package available here:
http://www.zope.org/Members/shh/ZopeTestCase

How to run the tests:

    Setup your Enviroment Variable and run the scripts:
  
        - set SOFTWARE_HOME to point to your Zope installation, e.g: /usr/lib/zope/lib/python/

        - if you use a zope instance setup set INSTANCE_HOME to your Zope instance, e.g: /var/lib/zope/instance/default/

        - run single test: python test_InterfaceTool.py

        - run test-suite: python runalltests.py

    Alternatively you may use the testrunner utility:

        - install testrunner.py from the ZopeTestCase Homepage and use it 

        - python /path/to/zope/utilities/testrunner.py -qa

        - run single test:'python /path/to/zope/utilites/testrunner.py -qif testMyCoolMachine.py'

        - run all tests:'python /path/to/zope/utilites/testrunner.py -qia
        
        - if this fails, you probably link your products into your instance, so use:
         
        python /path/to/zope/utilites/testrunner.py -qI /path/to/your/instance -f testMyCoolMachine.py 


How to setup a new unittest for a CMFPlone component:

    - Install ZopeTestCase

    - Install testrunner.py

    - copy one of the testSkeleton* files and give it a usefull name, starting with test, e.g: testMyCoolMachine.py

    - open the new script and change all instances of SomeProduct to the name of your Product.


How to use ZopeTestCase with a Plone/CMF based Products:

    - Install Plone

    - Install ZopeTestCase

    - Install testrunner.py

    - In your Product Directory create a directory 'tests'

    - copy the following files from CMFPlone/tests into your 'tests'

          - framework.py

          - runalltest.py

          - testSkeleton*.py

    - copy one of the testSkeleton* files and give it a usefull name, starting with test, e.g: testMyCoolMachine.py

    - open the new script and change all instances of SomeProduct to the name of your Product.

