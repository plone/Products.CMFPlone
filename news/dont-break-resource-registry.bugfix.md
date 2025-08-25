Make resource registry more robust against broken resources.

Don't break the resource registry when a resource error happens (missing
dependency, circular dependency, file not found, etc). Admins will see a
warning badge and can fix the problem in the resource registry user interface.
Previously such errors broke the rendering of the whole site, making fixes very
fiddly.
[thet]
