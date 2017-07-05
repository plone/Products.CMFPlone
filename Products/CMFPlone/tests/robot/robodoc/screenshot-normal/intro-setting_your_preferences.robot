========================
Setting Your Preferences
========================

.. include:: _robot.rst

After logging in to a Plone web site, you can change your personal preferences for information about your identity and choice of web site settings.

After logging in, your full name will show on the :term:`toolbar`.

Click on your name to open the sub-menu, then click on the *Preferences* link to go to your personal area:


.. code:: robotframework
   :class: hidden

   *** Test Cases ***


   Show menubar
       Go to  ${PLONE_URL}

       Click link  css=#portal-personaltools a

       Wait until element is visible
       ...  css=#portal-personaltools li.plone-toolbar-submenu-header

       Mouse over  personaltools-preferences
       Update element style  portal-footer  display  none

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/show-preferences.png
       ...  css=div.plone-toolbar-container
       ...  css=li.plone-toolbar-submenu-header

.. figure:: /_robot/show-preferences.png
   :align: center
   :alt: Show Preferences

.. code:: robotframework
   :class: hidden

   *** Test Cases ***


   Show personal preferences
       Go to  ${PLONE_URL}/@@personal-preferences

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/personal-preferences.png
       ...  css=#main-container


.. figure:: /_robot/personal-preferences.png
   :align: center
   :alt: Personal Preferences



Date entry fields include:

-  *Wysiwyg editor* - Plone comes standard with :term:`TinyMCE`, an easy to use graphical editor to edit texts, link to other content items and so forth. Your site administrator might have installed alternatives, though.
-  *Language* - On multilingual sites, you can select the language that you create content in most often. Plone excels at offering multilingual support.
-  *Time zone* - If you work in a different timezone than the server default, you can select it here.


Personal information
--------------------

Now let's switch over to the "Personal Information" tab:


.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show personal information
       Go to  ${PLONE_URL}/@@personal-information

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/personal-information.png
       ...  css=#main-container


.. figure:: /_robot/personal-information.png
   :align: center
   :alt: Personal Information




-  *Full Name*- If your name is common, include your middle initial or middle name.
-  *E-mail address* - REQUIRED - You may receive emails from the website system, or from a message board, if installed, etc. When an item is required, a little red dot will show alongside the item.
-  *Home page* web address - If you have your own web site or an area at a photo-sharing web site, for instance, enter the web address here, if you wish, so people can find out more about you.
-  *Biography* text box - Enter a short description of yourself here, about a paragraph or so in length.
-  *Location*  - This is the name of your city, town, state, province, or whatever you wish to provide.
-  *Portrait* photograph upload - The portrait photograph will appear as a small image or thumbnail-size image, so it is best to use a head shot or upper-torso shot for this.

You can change your preferences whenever you wish.


Changing your password
----------------------

The last tab allows you to change your password.

.. note::

   Plone is used by a variety of organisations. Some of these have centralized policies on where you can change your password, because this might also involve your access to other computer resources. In those cases, this screen might have been disabled.

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show personal information
       Go to  ${PLONE_URL}/@@change-password

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/change-password.png
       ...  css=#main-container


.. figure:: /_robot/change-password.png
   :align: center
   :alt: Change Password
