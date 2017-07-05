Adding Images
=============

.. include:: _robot.rst

Adding images to a Plone web site is a basic task that may involve a little work on your local computer, but is essential, because photographs, maps, and custom graphics are so important on web sites.

:doc:`preparing-images-for-the-web`

.. note::

    **Remember to use web-standard file formats for all images.
    Acceptable formats include: JPG, JPEG, GIF, and PNG.

    Do not use BMP or TIFF formats as these are not widely supported by web browsers, and can lead to slower websites.**


When you are ready to upload an image, use the *Add new...* drop-down menu.

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show add new image menu
       Go to  ${PLONE_URL}

       Wait until element is visible
       ...  css=span.icon-plone-contentmenu-factories
       Click element  css=span.icon-plone-contentmenu-factories

       Wait until element is visible
       ...  css=#plone-contentmenu-factories li.plone-toolbar-submenu-header

       Mouse over  image
       Update element style  portal-footer  display  none

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/adding-images_add-menu.png
       ...  css=div.plone-toolbar-container
       ...  css=#plone-contentmenu-factories ul


.. figure:: /_robot/adding-images_add-menu.png
   :align: center
   :alt: add-new-menu.png


After clicking to add an **Image**, you'll see the *Add Image* panel:

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show new image edit form
       Page should contain element  image
       Click link  image

       Wait until element is visible
       ...  css=#form-widgets-title

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/adding-images_add-form.png
       ...  css=#content

.. figure:: /_robot/adding-images_add-form.png
   :align: center
   :alt: Adding images form

The Title and Description fields (field, as in "data input field") are there, as with adding a Folder, and at the bottom there is a place to upload an image.
Let's look at the three input fields individually:

-  *Title* - Use whatever text you want, even with blanks and
   punctuation (Plone handles web addressing).
-  *Description* - Always a good idea, but always optional. Leave it
   blank if you want.
-  *Image* - The Image field is a text entry box along with a Browse...
   button. You don't have to type anything here; just click the Browse
   button and you'll be able to browse you local computer for the image
   file to upload.

For images, at a minimum, you will browse your local computer for the image file, then click **Save** at the bottom to upload the image to the Plone web site.

You'll have to wait a few seconds for the upload to complete.
A preview of the uploaded image will be shown when the upload has finished.

Images and files that you upload into Plone have their IDs (URLs) based on the title that you give to the image (instead of the file name of the image or file).

However, if you leave the title empty, the name of the item will default to the name of the file.
