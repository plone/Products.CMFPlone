Reordering Items
=====================

.. include:: _robot.rst

Using "Contents" on the Toolbar gives you the overview of a folder. From here, you can do manual reordering of items in a folder.


.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Edit folder
       Go to  ${PLONE_URL}
       Click element  css=#contentview-folderContents a
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/foldercontents-reorder.png
       ...  css=#content

.. figure:: /_robot/foldercontents-reorder.png
   :align: center
   :alt: reordering content

   Simply hover over the content item you want to reorder (any column is fine, just don't hover exactly over the title), and the cursor changes into a hand. Click and drag to reorder.