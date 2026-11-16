Freeze security declarations when Zope has started, when AccessControl supports this.
After this, no code can make more modules, classes or types accessible from restricted code, for example with `allow_module` or `allow_class`.
Dangerous modules like `os` and `subprocess` that are fully accessible from restricted code are logged as a warning.
Besides the dangerous modules that AccessControl checks, Plone also checks `plone.api.env`, which can switch to another user or roles, and `plone.protect`, which can disable CSRF protection.
@mauritsvanrees
