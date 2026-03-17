Resource registry: Allow to use `*` dependencies.

In #4076, #4077 and #4054 we added the `all` keyword for the `depends`
attribute of resource registry entries to define a resource which should be
loaded after all other. In Plone < 6 we had the `*` keyword for exactly that.
This brings now back `*` in addition to `all` for the same purpose. This might
also allow for a smoother upgrade experience.
[thet]
