from Products.CMFPlone import PloneMessageFactory as _
from zope import schema
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import zope.component
import zope.interface


OVERRIDE_RESOURCE_DIRECTORY_NAME = "resource_overrides"


class IResourceRegistry(zope.interface.Interface):

    # DEPRECATED

    url = schema.ASCIILine(title=_("Resources base URL"), required=False)

    js = schema.ASCIILine(title=_("Main js file"), required=False)

    css = schema.List(
        title=_("CSS/LESS files"),
        value_type=schema.ASCIILine(title=_("URL")),
        default=[],
        required=False,
    )

    init = schema.ASCIILine(title=_("Init instruction for shim"), required=False)

    deps = schema.ASCIILine(
        title=_("Dependencies for shim"),
        description=_("Comma separated values of resource for shim"),
        required=False,
    )

    export = schema.ASCIILine(title=_("Export vars for shim"), required=False)

    conf = schema.Text(
        title=_("Configuration in JSON for the widget"),
        description=_("Should be accessible on @@getWCconfig?id=name"),
        required=False,
    )


class IBundleRegistry(zope.interface.Interface):

    jscompilation = schema.ASCIILine(
        title=_("URL of the last js compilation"), required=False
    )

    csscompilation = schema.ASCIILine(
        title=_("URL of the last css compilation"), required=False
    )

    expression = schema.ASCIILine(
        title=_("Expression to render"),
        description=_(
            "In case its a bundle we can have a condition to render it (it "
            "does not apply if the bundle is merged)."
        ),
        required=False,
    )

    enabled = schema.Bool(title=_("It's enabled?"), default=True, required=False)

    depends = schema.ASCIILine(
        title=_("Depends on another bundle"),
        description=_(
            "In case you want to be the last: *, in case its the first should be empty"
        ),
        required=False,
    )

    load_async = schema.Bool(
        title=_("Load asynchronously"),
        description=_(
            "Load the JavaScript files asynchronously by adding an ``async`` attribute to the script tag."
        ),
        default=False,
        required=False,
    )

    load_defer = schema.Bool(
        title=_("Load deferred"),
        description=_(
            "Load the JavaScript files deferred after the document has been parsed but before ``DOMContentLoaded`` by adding a ``defer`` attribute to the script tag."
        ),
        default=False,
        required=False,
    )

    # DEPRECATED IN Plone 6, for now keep for BBB
    compile = schema.Bool(
        title=_("(DEPRECATED) Does your bundle contains any RequireJS or LESS file?"),
        description=_(
            "If its true and you modify this bundle you need to build it before production"
        ),
        default=True,
        required=False,
    )

    resources = schema.List(
        title=_("(DEPRECATED) Loaded resources"),
        description=_(
            "The resources that are going to be loaded on this bundle in order"
        ),
        value_type=schema.ASCIILine(title=_("Resource name")),
        required=False,
    )

    last_compilation = schema.Datetime(
        title=_("(DEPRECATED) Last compiled date"),
        description=_("Date time of the last compilation of this bundle"),
        required=False,
    )

    develop_javascript = schema.Bool(
        title=_("(DEPRECATED) Develop JavaScript"), default=False
    )

    develop_css = schema.Bool(title=_("(DEPRECATED) Develop CSS"), default=False)

    stub_js_modules = schema.List(
        title=_("(DEPRECATED) Stub JavaScript modules"),
        description=_(
            "Define list of modules that will be defined empty "
            "on RequireJS build steps to prevent loading modules multiple times."
        ),
        value_type=schema.ASCIILine(title=_("Resource name")),
        required=False,
        missing_value=[],
        default=[],
    )

    merge_with = schema.Choice(
        title=_("(DEPRECATED) Merge with"),
        description=_(
            "In production mode, bundles are merged together to reduce the "
            "quantity of JS and CSS resources loaded by the browser. Choose "
            "'default' if this bundle must be available for all the visitors, "
            "choose 'logged-in' if it must be available for logged-in users "
            "only, or leave it empty if it must not be merged."
        ),
        vocabulary=SimpleVocabulary(
            [
                SimpleTerm("", "", _("")),
                SimpleTerm("default", "default", "default"),
                SimpleTerm("logged-in", "logged-in", "logged-in"),
            ]
        ),
        default="",
        required=False,
    )
