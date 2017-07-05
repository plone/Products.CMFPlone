Inserting Tables
================

.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show TinyMCE insert tables
       Go to  ${PLONE_URL}
       Click element  css=#contentview-edit a
       Wait until element is visible
       ...  css=#mceu_16-body

       Click element  css=#mceu_21 button
       Mouse over  css=#mceu_44
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/tinymce-table.png
       ...  css=#content

Tables are handy for tabular data and lists.

To add a table, put your cursor where you want it and click the *Table* dropdown menu.

.. figure:: /_robot/tinymce-table.png
   :align: center
   :alt: TinyMCE table

There are various options to choose a *style* for the table, insert rows and columns, and set properties on the individual cells. Plone comes with a few basic styles for tables, but you (or your site administrator) will most likely want to provide some extra CSS classes to make them look better.

.. note::

   Creating and managing tables in HTML has historically been *awkward*. People tend to mis-use them for layout purposes, which you should not do.

   Use tables **only** for tabular data. And, as rule of thumb, try to keep it to a very small number of rows and columns.

   If you want to present information that is mostly tabular, such as larger amounts of statistical data, there are various add-ons to help you do that. These will generate nicer tables, and are easier to work with both for content editors and visitors to your site. Visitors will be able to sort tables and use a quick search to locate individual cells, for instance.