Editing Content
===============

.. include:: _robot.rst

Editing Plone content works the same as adding content -- usually the data entry and configuration panels for the content are the same for editing as for adding.

Of course, when we edit an item of content, the item already exists.
Click "Edit" on the toolbar when you are viewing it, and you will see the data entry panel for the item, along with the existing values of the item's data.

For an example of something really simple, where editing looks the same as adding, we can review how to edit the default frontpage on a new Plone site.

The *Edit* panel for a Page shows the title, description and text areas.

.. note::

    If you do wish to give a description, which is a generally a good idea, the description can be text only -- there is no opportunity for setting styling of text, such as bold, italics, or other formatting. This keeps the descriptions of Plone content items as simple as possible, and is also required by the :term:`Dublin Core` standard.


.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Edit folder
       Go to  ${PLONE_URL}
       Click element  css=#contentview-edit a
       Wait until element is visible
       ...  css=#mceu_16-body
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/edit-page.png
       ...  css=#content

.. figure:: /_robot/edit-page.png
   :align: center
   :alt: Editing a page

That's it. Change what you want, for instance changing the description or the content, and save.
The content item will be updated in Plone's storage system.
You can repeatedly edit content items, just as you can repeatedly edit files on your local computer.



.. note::

    Note that there is an extra field, called **Change Note**.
    Here you can write a short message on why you were editing this, like "updated with our new company motto".
    That note will normally not be shown on a public website, but is available for your co-workers to see when they look at the history of a content item.



