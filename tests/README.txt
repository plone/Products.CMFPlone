
CMFPlone tests depend on the ZopeTestCase package available here:
http://www.zope.org/Members/shh/ZopeTestCase

Tests may be run individually or as a mega-suite:

    - python test_InterfaceTool.py

    - python runalltests.py

Alternatively you may use the testrunner utility:

    - python /Zope/utilities/testrunner.py -qa


How to use ZopeTestCase with your Plone/CMF based Products:

  - Install Plone

  - Install ZopeTestCase

  - Install testrunner.py
  
  - In your Product Directory create a directory 'tests'

  - copy the following files from CMFPlone/tests into your 'tests'

      - framework.py

      - runalltest.py

      - testSkeletonPloneTest.py

      - testSkeletonCMFTest.py

      - testSkeletonZopeTest.py

  - copy one of the testSkeleton* files and give it a usefull name, starting with test, e.g: testMyCoolMachine.py

  - open the new script and edit it.

  - to run the tests, either setup your enviroment:
  
    - set SOFTWARE_HOME to point to your Zope installation, e.g: /usr/lib/zope/lib/python/

    - set INSTANCE_HOME to your Zope instance, e.g: /var/lib/zope/instance/default/

    - run single test:'python testMyCoolMachine.py'

    - run all tests:'runalltest.py'

  - or install testrunner.py from the ZopeTestCase Homepage and use it 

    - run single test:'python /path/to/zope/utilites/testrunner.py -qif testMyCoolMachine.py'

    - run all tests:'python /path/to/zope/utilites/testrunner.py -qia
    
    - if this fails, you probably link your products into your instance, so use:
     
    - python /path/to/zope/utilites/testrunner.py -qI /path/to/your/instance -f testMyCoolMachine.py 

