Inserting Images
=====================

.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show TinyMCE image
       Go to  ${PLONE_URL}
       Click element  css=#contentview-edit a
       Wait until element is visible
       ...  css=#mceu_16-body
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/tinymce-imgbutton.png
       ...  css=#mceu_15

       Click element  css=#mceu_15 button
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/tinymce-imgdialog.png
       ...  css=div.plone-modal-content


The TinyMCE editor allows you to insert image files stored in Plone into your document, using the Image button on the TinyMCE toolbar:

.. figure:: /_robot/tinymce-imgbutton.png
   :align: center
   :alt:

Clicking this button launches the Insert Image dialog:

.. figure:: /_robot/tinymce-imgdialog.png
   :align: center
   :alt:

There are three ways to select images:

Internal image
   This means the image is already on the site somewhere. You can search on it by title or description, or navigate to it.
Upload
   This means using an image file you already have on your computer. The image will be uploaded to the same folder as the content item you are editing.
External Image
   This means specifying the URL of an image that is elsewhere on the web.

For all three methods, you can set the Title, ALT text (this is important for non-sighted users, make this a description of the image) and the alignment. Aligning "inline" means the image will appear exactly where you put it, in the middle of a sentence if wanted. Aligning "left" or "right" will make the image go to the side of the paragraph, and text will flow around it.

For Internal and Uploaded images, you can also select the size. These sizes come from the range of sizes that you (or your site administrator) has set in the :doc:`control panel </adapt-and-extend/config/index>`. Plone automatically generates the different sizes when you upload an image.

.. note::

   Be careful with the size "original". Modern cameras and smartphones take high-resolution pictures, much higher than is usually needed in a website. Larger pictures take longer to download, making your site slower to appear.
