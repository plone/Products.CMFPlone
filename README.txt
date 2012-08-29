Introduction
============

This package provide the registration form for new users using a Zope formlib_
form. It allows the site administrator to select fields from a schema to
appear on the registration form.

Example below is extracted from the addon `collective.examples.userdata`_

How to Override the default schema
==================================


The default schema is provided by a utility.

You can override this utility by using GenericSetup in your addon:
add a componentregistry.xml file::

    <?xml version="1.0"?>
    <componentregistry>
      <utilities>
        <utility
          interface="plone.app.users.userdataschema.IUserDataSchemaProvider"
          factory="collective.examples.userdata.userdataschema.UserDataSchemaProvider"
        />
      </utilities>
    </componentregistry>

and declare your utility in a configure.zcml file::

    <utility
      interface="plone.app.users.userdataschema.IUserDataSchemaProvider"
      factory="collective.examples.userdata.userdataschema.UserDataSchemaProvider"

A ``userdataschema.py`` file should contains::

    from plone.app.users.userdataschema import IUserDataSchemaProvider
    from plone.app.users.userdataschema import IUserDataSchema


    class UserDataSchemaProvider(object):
        implements(IUserDataSchemaProvider)

        def getSchema(self):
            """
            """
            return IEnhancedUserDataSchema


    class IEnhancedUserDataSchema(IUserDataSchema):
        """ Use all the fields from the default user data schema, and add various
        extra fields.
        """

For example you can add a country field to the schema::

    class IEnhancedUserDataSchema(IUserDataSchema):
        # ...
        country = schema.TextLine(
            title=_(u'label_country', default=u'Country'),
            description=_(u'help_country',
                          default=u"Fill in which country you live in."),
            required=False,
            )

An other use case could be a not stored field.
For example an "Accept Terms" field can be implemented by adding a
``constraint`` to the schema::

    def validateAccept(value):
        if not value == True:
            return False
        return True

    class IEnhancedUserDataSchema(IUserDataSchema):
        # ...
        accept = schema.Bool(
            title=_(u'label_accept', default=u'Accept terms of use'),
            description=_(u'help_accept',
                          default=u"Tick this box to indicate that you have found,"
                          " read and accepted the terms of use for this site. "),
            required=True,
            constraint=validateAccept,
            )

Because this field can be ignored once registration is complete, you don't add
it to the memberdata properties and voila.

Next you have to add theses fields to the memberdata properties using
a memberdata_properties.xml::

    <?xml version="1.0"?>
    <object name="portal_memberdata" meta_type="Plone Memberdata Tool">
     <property name="country" type="string"></property>
    </object>


How to define which fields should appear on the registration form
=================================================================

Fields which appear on the registration form are defined in the
site_properties property sheet::

    <?xml version="1.0"?>
    <object name="portal_properties" meta_type="Plone Properties Tool">
     <object name="site_properties" meta_type="Plone Property Sheet">
      <!-- Fields that will be on the form after installation of the product -->
      <property name="user_registration_fields" type="lines">
       <element value="country" />
       <element value="accept" />
      </property>
     </object>
    </object>

The site manager can modify this configuration using the control panel
@@member-registration.

How to update the personal information form
===========================================

In order to see these properties in the Personal Information form
(`@@personal-information`), you need to take a few extra steps. You have to
override the default adapter which adapts a user object to a form. See the
plone.app.controlpanel_ documentation for a detailed explanation.

To override plone.app.users' default adapter, you have to put this in
`overrides.zcml`::

  <adapter 
    provides=".userdataschema.IEnhancedUserDataSchema"
    for="Products.CMFCore.interfaces.ISiteRoot"
    factory=".adapter.EnhancedUserDataPanelAdapter"
    />

In `adapter.py`, repeat (yes, this is unfortunate) the fields we defined in
the schema. For example, for the `firstname` field, we do this::

    class EnhancedUserDataPanelAdapter(UserDataPanelAdapter):
        """
        """
        def get_firstname(self):
            return self.context.getProperty('firstname', '')
        def set_firstname(self, value):
            return self.context.setMemberProperties({'firstname': value})
        firstname = property(get_firstname, set_firstname)

.. _formlib: http://pypi.python.org/pypi/zope.formlib
.. _plone.app.controlpanel: http://pypi.python.org/pypi/plone.app.controlpanel
.. _`collective.examples.userdata`: http://pypi.python.org/pypi/collective.examples.userdata
