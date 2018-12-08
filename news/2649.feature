- Add ``load_async`` and ``load_defer`` attributes to resource registries bundle settings.
  When set, ``<script>`` tags are rendered with ``async="async"`` resp. ``defer="defer"`` attributes.
  You also need to empty the ``merge_with`` property of your bundle, because production bundles (``default.js`` and ``logged-in.js``) are never loaded with async or defer.
  The default.js includes jQuery and requirejs and those are needed at many places and therefore cannot be loaded asynchronously.
  Refs: #2649, #2657.
  [thet]
