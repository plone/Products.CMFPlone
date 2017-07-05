.. code:: robotframework

   *** Settings ***

   Resource  plone/app/robotframework/server.robot
   Resource  plone/app/robotframework/keywords.robot
   Resource  Selenium2Screenshots/keywords.robot

   Library  OperatingSystem

   Suite Setup  Run keywords  Suite Setup  Test Setup
   Suite Teardown  Run keywords  Test teardown  Suite Teardown

   *** Variables ***

   ${FIXTURE}  plone.app.robotframework.PLONE_ROBOT_TESTING
   @{DIMENSIONS}  1024  768
   @{APPLY_PROFILES}  plone.app.contenttypes:plone-content


   *** Keywords ***

   Suite Setup
       Run keyword if  not sys.argv[0].startswith('bin/robot')
       ...             Setup Plone site  ${FIXTURE}
       Run keyword if  sys.argv[0].startswith('bin/robot')
       ...             Open test browser
       Run keyword and ignore error  Set window size  @{DIMENSIONS}

   Test Setup
       Import library  Remote  ${PLONE_URL}/RobotRemote

       Run keyword if  sys.argv[0].startswith('bin/robot')
       ...             Remote ZODB SetUp  ${FIXTURE}

       ${language} =  Get environment variable  LANGUAGE  'en'
       Set default language  ${language}

   Test Teardown
       Run keyword if  sys.argv[0].startswith('bin/robot')
       ...             Remote ZODB TearDown  ${FIXTURE}

   Suite Teardown
       Run keyword if  not sys.argv[0].startswith('bin/robot')
       ...             Teardown Plone Site
       Run keyword if  sys.argv[0].startswith('bin/robot')
       ...             Close all browsers
