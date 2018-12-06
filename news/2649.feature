- Add ``load_async`` and ``load_defer`` attributes to resource registries bundle settings.
  When set, ``<script>`` tags are rendered with ``async="async"`` resp. ``defer="defer"`` attributes.
  In production mode, the setting from the ``plone`` resp. ``plone-logged-in`` bundles are used for the ``default`` resp. ``logged-in`` meta bundles (``merge_with`` setting). 
  [thet]
