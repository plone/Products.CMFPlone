This folder contains the files required if you want to have 
Plone use a main layout without tables.

For those of you who were running tableless designs in the RC3 
and earlier releases and want to keep it that way: the Directory 
View is added via migration. To (re)enable:

- Switch to the 'Plone Tableless' Skin (after Migration).

- You can customize the templates in this folder, this will
  make them override the table-based ones.
 
- Add 'plone_tableless' to the layers of your skin.

This will activate the tableless versions of:

- main_template

- ploneColumns.css

- colophon

Apart from adding these two templates, no other changes are needed.
