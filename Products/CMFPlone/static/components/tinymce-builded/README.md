tinymce-builded
===============

>Biulded version of [TinyMCE](https://github.com/tinymce/tinymce) editor.

Also available as a Bower package `tinymce-builded`. You can install it by `bower install tinymce-builded`

### TinyMCE version update process

1. Create new branch from latest `master` and give it a name `update-X.X.X` where `X.X.X` is the version number of TinyMCE that you are updating to
2. Download latest Dev package of TinyMCE from [official download page](https://www.tinymce.com/download/) and extract it to any folder
3. Navigate to the extracted `tinymce` directory and copy `tinymce/js` folder to `tinymce_builded/` root folder rewriting existing files
4. Download latest language files from [Language Packages page](https://www.tinymce.com/download/language-packages/) and extract it to any folder
5. Copy the extracted `langs` folder to `tinymce_builded/js/tinymce/` replacing existing files
6. Update version field in `bower.json` according to TinyMCE version (it should be the same)
7. Stage all files in git: `git add --all .`
8. Commit changes: `git commit -m "Update to X.X.X"`
9. Tag the commit with a new version: `git tag X.X.X`
10. Push the branch to github including tags: `git push origin update-X.X.X --tags`
11. Create a pull-request against `master` branch and merge it

That's it!