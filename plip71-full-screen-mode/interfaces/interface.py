try:
    # Zope >= 2.6
    from Interface import Interface, Attribute
except ImportError:
    # Zope < 2.6
    from Interface import Base as Interface, Attribute
