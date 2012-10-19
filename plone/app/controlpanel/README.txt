Introduction
============

This package provides various control panels for Plone and some infrastrucuture
to make it as easy as possible to create those with the help of zope.formlib.

The general approach taken is to re-use as much of formlib as possible. This
lead to the decision to use formlib's EditForm's functionality, as these
provide the most automation found in formlib today.

As a result of this decision we needed to take a slightly unconventional
approach as EditForm's only work on one single context, as they are targeted
at editing content objects, which usually are available as one context only.

Control panels on the other side most commonly present settings from various
sources and group these in a user-friendly way. In order to still be able to use
EditForm's we introduce one abstract adapter as a middleware layer per control
panel, that is used as the one context formlib's EditForm's need but internally
pulls in the various settings from all the possible sources and pushes them back
to the right places again.

Following this approach a control panel consists of at least three classes:

- An interface that describes the settings to be available in the control
  panel with the help of zope.schema. This gives us automatic type checking
  and some other basic validation of the settings. It also lets us specify
  vocabularies to be used for Choice-type properties.

- An adapter implementing the above interface, exposing all the different
  settings as properties. As we don't want to have those control panels
  available all over the place, we restrict them to adapt the 'IPloneSiteRoot'
  only. Sometimes we use the 'SchemaAdapterBase' class from CMFDefault.formlib
  and the property wrapper 'ProxyFieldProperty' to automatically convert the
  values found in our site to the types expected by formlib and vica versa.
  For example we often need to store tuples while formlib expects sets, store
  encoded strings in site encoding rather than unicode or use Zope2's DateTime
  class instead of Python's datetime package.

- And finally the form itself. We can use the common base class
  'ControlPanelForm' to provide us with a consistent look and feel for all
  control panels. This is accomplished by using the 'control-panel.pt'
  template. For most cases this should be the only template that needs to be
  written.

  The 'ControlPanelForm' also provides us with two common actions and as a
  side effect overrides the 'handle_edit_action' in a Zope2-compatible way,
  where the default implementation needs the current locale to be present as
  part of the REQUEST, which is not the case in a Zope2 environment so far.

  The form is also the place to specify custom widgets for some properties.
  There are some custom widgets available in the widgets.py module in this
  package.

While the above-mentioned works pretty well for simple cases it is not yet clear
if it will work for complex control panels in the same way. Especially forms
that use a multitude of actions (for example user/group management) or consist
of more than one 'tab' (for example kupu but also smart folder settings) are not
easily implemented so far.

Hopefully we will be able to provide common helper classes and templates for
those complex cases as well, though.

