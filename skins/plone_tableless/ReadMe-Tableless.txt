This folder contains the files required if you want to have 
Plone use a main layout without tables.

To enable, put 'plone_tableless' near the top in your skinpath,
after 'custom'.

You can also customize the templates in this folder, this will 
also make them override the table-based ones.

For those of you who were running tableless designs in the RC3 
and earlier releases and want to keep it that way - simply add
a DirectoryView for 'plone_tableless' in 'portal_skins', and 
add it to the skinpath. This will activate the tableless versions
of:

- main_template

- ploneColumns.css

Apart from adding these two templates, no other changes are needed.
