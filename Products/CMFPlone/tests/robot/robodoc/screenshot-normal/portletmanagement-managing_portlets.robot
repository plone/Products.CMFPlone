Managing Portlets
=================

To assign the different :doc:`types of portlet <portlet-types>` into your site, use the "Manage portlets" item on the Toolbar.

There are three locations where portlets can be put: to the left, to the right, and in the footer.

.. note::

   The "left", "right" and "footer" locations come from the classical website design. It is entirely possible, using Diazo theming, to move these portlet locations from one place to another. In fact, many so-called *responsive* designs, that automatically scale for mobile devices, will not display these as 'left' and 'right'.

   There is still a relevance to these different locations, even on mobile devices: as a rule of thumb, the 'left' portlets will be displayed **before** the main content, and the 'right' portlets afterwards, with the 'footer' portlets last.

.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show portlet management
       Go to  ${PLONE_URL}
       Click link  css=#plone-contentmenu-portletmanager a

       Wait until element is visible
       ...  css=#plone-contentmenu-portletmanager li.plone-toolbar-submenu-header

       Update element style  portal-footer  display  none

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/portlet-menu.png
       ...  css=div.plone-toolbar-container
       ...  css=#content-header

   Show right portlets
       Go to  ${PLONE_URL}/@@topbar-manage-portlets/plone.footerportlets

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/portlet-footer.png
       ...  css=#content



.. figure:: /_robot/portlet-menu.png
   :align: center
   :alt: Where to find the Portlet menu on the Toolbar

From here, you choose which region you want to work on. In the example below, we are working on the "footer portlets"

.. note::

   The footer portlet region is new for Plone 5. If you have worked on previous versions of Plone: this is where you now can find (and edit) the colophon and other items.

.. figure:: /_robot/portlet-footer.png
   :align: center
   :alt: List of footer portlets


The various options for "blocking" are explained in the :doc:`Portlet hierarchy <portlet-hierarchy>` section.

Adding a Portlet
----------------

Adding a Portlet is as simple as selecting the **Add Portlet** drop down box and clicking on the type of Portlet you would like to add.
We will cover the different options available in the :doc:`next section <portlet-types>`.

Editing an Existing Portlet
---------------------------

To edit the properties of an existing Portlet, simply click on the name of the Portlet.
If we wanted to edit the properties of the Navigation Portlet, we would Click on *Navigation*.
Each type of Portlet will have different configuration options available to it.

Rearranging Portlets
--------------------

To rearrange your Portlets, simply click the **up or down arrow**.
This will affect the order your Portlets are displayed on the page.

Removing Portlets
-----------------

To remove a Portlet, click the **"X"** associated with its name.

Hiding Portlets
---------------

You can show/hide portlets using the associated show/hide link.


Adding multiple portlets
------------------------

With Portlets, you can add more than one of the same type on a page.
There is no limit (except common sense) to how many times you can use an individual Portlet or a limit to how many total Portlets can be on a Page.
