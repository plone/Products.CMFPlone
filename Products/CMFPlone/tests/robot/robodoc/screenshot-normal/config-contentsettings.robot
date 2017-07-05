.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show Content setup screen
       Go to  ${PLONE_URL}/@@content-controlpanel
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/content-setup.png
       ...  css=#content

       Click element  type_id

       Select From List  name=type_id  Document

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/content-document.png
       ...  css=#content


