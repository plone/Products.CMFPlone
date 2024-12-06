Allow bundles to be rendered after all others.

JS and CSS resources can now be rendered after all other resources in their
resource group including the theme (e.g. the Barceloneta theme CSS).

There is an exception for custom CSS which can be defined in the theming
controlpanel. This one is always rendered as last style resource.

To render resources after all others, give them the "depends" value of "all".
For each of these resources, "all" indicates that the resource depends on all other resources, making it render after its dependencies.
If you set multiple resources with "all", then they will render alphabetically after all other.

This lets you override a theme with custom CSS from a bundle instead of having
to add the CSS customizations to the registry via the "custom_css" settings.
As a consequence, theme customization can now be done in the filesystem in
ordinary CSS files instead of being bound to a time consuming workflow which
involves upgrading the custom_css registry after every change.
[thet, petschki]
