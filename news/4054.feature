Allow bundles to be rendered after all others.

JS and CSS resources can now be rendered after all other resources in their
resource group including the theme (e.g. the Barceloneta theme CSS).

There is an exception for custom CSS which can be defined in the theming
controlpanel. This one is always rendered as last style resource.

To render resources after all others, give them the "depends" value of "all".
indicates that the resource depends on all other being rendered before. The
resource is then rendered as last resource of it's resource group.

This allows to override a theme with custom CSS from a bundle instead of having
to add the CSS customizations to the registry via the "custom_css" settings.
As a consequence, theme customization can now be done in the filesystem in
ordinary CSS files instead of being bound to a time consuming workflow which
involves upgrading the custom_css registry after every change.
[thet, petschki]
