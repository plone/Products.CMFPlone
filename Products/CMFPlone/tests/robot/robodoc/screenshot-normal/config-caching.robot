.. .. include:: _robot.rst

.. .. code:: robotframework
..    :class: hidden

..   *** Test Cases ***

..   Show caching setup screen
       Go to  ${PLONE_URL}/@@caching-controlpanel
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/caching-setup.png
       ...  css=#content
