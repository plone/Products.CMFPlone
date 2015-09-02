from Products.CMFCore.FSFile import FSFile
from Products import CMFPlone
from Products.CMFPlone.interfaces import (
    IBundleRegistry,
    IResourceRegistry)

from Products.Five.browser.resource import FileResource
from Products.Five.browser.resource import DirectoryResource

import os
import json
from plone.registry.interfaces import IRegistry

from plone.resource.directory import FilesystemResourceDirectory
from plone.resource.file import FilesystemFile

from plone.subrequest import subrequest
import uuid
from zope.component import getUtility


# some initial script setup
if 'SITE_ID' in os.environ:
    site_id = os.environ['SITE_ID']
else:
    site_id = 'Plone'
print('Using site id: ' + site_id)

portal = app[site_id]  # noqa
from zope.site.hooks import setSite
setSite(portal)

# start the juicy stuff
temp_resource_folder = 'temp_resources'
registry = getUtility(IRegistry)
bundles = registry.collectionOfInterface(
    IBundleRegistry, prefix="plone.bundles", check=False)
resources = registry.collectionOfInterface(
    IResourceRegistry, prefix="plone.resources", check=False)  # noqa
lessvariables = registry.records['plone.lessvariables'].value

gruntfile_template = """
module.exports = function(grunt) {{
    'use strict';
    grunt.initConfig({{
        pkg: grunt.file.readJSON('package.json'),
        less: {{
            {less}
        }},
        requirejs: {{
            {requirejs}
        }},
        sed: {{
            {sed}
        }},
        uglify: {{
            {uglify}
        }},
        watch: {{
            scripts: {{
                files: {files},
                tasks: ['requirejs', 'less', 'sed', 'uglify']
            }}
        }}
    }});

    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-requirejs');
    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-sed');

    grunt.registerTask('default', ['watch']);
    grunt.registerTask('compile-all', ['requirejs', 'less', 'sed', 'uglify']);
    {bundleTasks}
}}
"""

sed_config = """
    {name}: {{
      path: '{path}',
      pattern: '{pattern}',
      replacement: '{destination}',
    }},
"""

requirejs_config = """
            "{bkey}": {{
                options: {{
                    baseUrl: '/',
                    generateSourceMaps: false,
                    preserveLicenseComments: false,
                    paths: {paths},
                    shim: {shims},
                    wrapShim: true,
                    name: '{name}',
                    exclude: ['jquery'],
                    out: '{out}',
                    optimize: "none"
                }}
            }},
"""
uglify_config = """
        "{bkey}": {{
          options: {{
            sourceMap: true,
            sourceMapName: '{destination}.map',
            sourceMapIncludeSources: false
          }},
          files: {{
            '{destination}': {files}
          }}
        }},
"""

less_config = """
            "{name}": {{
                options: {{
                    paths: {less_paths},
                    strictMath: false,
                    sourceMap: true,
                    outputSourceFiles: true,
                    strictImports: false,
                    sourceMapURL: "{sourcemap_url}",
                    sourceMapBasepath: "{base_path}",
                    relativeUrls: true,
                    plugins: [
                        new require('less-plugin-inline-urls'),
                    ],
                    modifyVars: {{
                      {globalVars}
                    }}
                }},
                files: {{
                    {files}
                }}
            }}
"""


def resource_to_dir(resource, file_type='.js'):
    if resource.__module__ == 'Products.Five.metaclass':
        try:
            return resource.chooseContext().path
        except:
            try:
                return resource.context.path
            except:
                try:
                    if callable(resource):
                        file_name = uuid.uuid4().hex
                        try:
                            os.mkdir(temp_resource_folder)
                        except OSError:
                            pass
                        full_file_name = temp_resource_folder + '/' + file_name + file_type  # noqa
                        temp_file = open(full_file_name, 'w')
                        temp_file.write(resource().encode('utf-8'))
                        temp_file.close()

                        return os.getcwd() + '/' + full_file_name
                    else:
                        print "Missing resource type"
                        return None
                except:
                    print "Missing resource type"
                    return None
    elif isinstance(resource, FilesystemFile):
        return resource.path
    elif isinstance(resource, FileResource):
        return resource.chooseContext().path
    elif isinstance(resource, DirectoryResource):
        return resource.context.path
    elif isinstance(resource, FilesystemResourceDirectory):
        return resource.directory
    elif isinstance(resource, FSFile):
        return resource._filepath
    else:
        print "Missing resource type"
        return None

# REQUIRE JS CONFIGURATION

paths = {}
shims = {}
for requirejs, script in resources.items():
    if script.js:
        # Main resource js file
        resource_file = portal.unrestrictedTraverse(script.js, None)
        src = None
        if resource_file:
            local_file = resource_to_dir(resource_file)
        else:
            # In case is not found on traverse we dump it from request to file
            response = subrequest(portal.absolute_url() + '/' + script.js)
            local_file = None
            if response.status == 200:
                js_body = response.getBody()
                file_name = uuid.uuid4().hex
                try:
                    os.mkdir(temp_resource_folder)
                except OSError:
                    pass
                local_file = temp_resource_folder + '/' + file_name + '.js'
                temp_file = open(local_file, 'w')
                temp_file.write(js_body.encode('utf-8'))
                temp_file.close()

        if local_file:
            # Extract .js
            paths[requirejs] = local_file[:-3]
            exports = script.export
            deps = script.deps
            inits = script.init
            if exports != '' or deps != '' or inits != '':
                shims[requirejs] = {}
                if exports != '' and exports is not None:
                    shims[requirejs]['exports'] = exports
                if deps != '' and deps is not None:
                    shims[requirejs]['deps'] = deps.split(',')
                if inits != '' and inits is not None:
                    shims[requirejs]['init'] = inits
        else:
            print "No file found: " + script.js
    if script.url:
        # Resources available under name-url name
        paths[requirejs + '-url'] = resource_to_dir(portal.unrestrictedTraverse(script.url))  # noqa


# LESS CONFIGURATION

globalVars = {}
globalVars["sitePath"] = "'/'"
globalVars["isPlone"] = "false"
globalVars["isMockup"] = "false"
globalVars['staticPath'] = "'" + os.path.join(
    os.path.dirname(CMFPlone.__file__),
    'static') + "'"

less_vars_params = {
    'site_url': 'LOCAL',
}

# Storing variables to use them on further vars
for name, value in lessvariables.items():
    less_vars_params[name] = value

for name, value in lessvariables.items():
    t = value.format(**less_vars_params)
    if 'LOCAL' in t:
        t_object = portal.unrestrictedTraverse(str(t.replace('LOCAL/', '').replace('\\"', '')), None)  # noqa
        if t_object:
            t_file = resource_to_dir(t_object)
            t_file = t_file.replace(os.getcwd() + '/', '')
            globalVars[name] = "'%s/'" % t_file
        else:
            print "No file found: " + str(t.replace('LOCAL/', '').replace('\\"', ''))  # noqa
    else:
        globalVars[name] = t

# Path to search for less
less_paths = []

# To replace later with sed
less_directories = {}

for name, value in resources.items():
    for css in value.css:
        # less vars can't have dots on it
        local_src = portal.unrestrictedTraverse(css, None)
        extension = css.split('.')[-1]
        if local_src:
            local_file = resource_to_dir(local_src, file_type=extension)
        else:
            # In case is not found on traverse we dump it from request to file
            response = subrequest(portal.absolute_url() + '/' + css)
            local_file = None
            if response.status == 200:
                css_body = response.getBody()
                file_name = uuid.uuid4().hex
                try:
                    os.mkdir(temp_resource_folder)
                except OSError:
                    pass
                local_file = temp_resource_folder + '/' + file_name + '.js'
                temp_file = open(local_file, 'w')
                temp_file.write(css_body.encode('utf-8'))
                temp_file.close()

        if local_file:
            less_directories[css.rsplit('/', 1)[0]] = local_file.rsplit('/', 1)[0].replace(os.getcwd() + '/', '')  # noqa
            # local_file = local_file.replace(os.getcwd(), '')
            # relative = ''
            # for i in range(len(local_file.split('/'))):
            #     relative += '../'
            # globalVars[name.replace('.', '_')] = "'%s'" % local_file  # noqa
            globalVars[name.replace('.', '_')] = "'%s'" % local_file.split('/')[-1]  # noqa
            if '/'.join(local_file.split('/')[:-1]) not in less_paths:
                less_paths.append('/'.join(local_file.split('/')[:-1]))
        else:
            print "No file found: " + css

globalVars_string = ""
for g, src in globalVars.items():
    globalVars_string += "\"%s\": \"%s\",\n" % (g, src)

# BUNDLE LOOP

require_configs = ""
uglify_configs = ""
less_configs = []
sourceMap_url = ""
sed_config_final = ""
watch_files = []
sed_count = 0
bundle_grunt_tasks = ""

for bkey, bundle in bundles.items():
    if bundle.compile:
        less_files = []
        js_files = []
        js_resources = []
        for resource in bundle.resources:
            res_obj = resources[resource]
            if res_obj.js:
                js_object = portal.unrestrictedTraverse(res_obj.js, None)
                if js_object:
                    main_js_path = resource_to_dir(js_object)
                    target_path = resource_to_dir(portal.unrestrictedTraverse(res_obj.js))
                    target_path = '/'.join(target_path.split('/')[:-1])
                    watch_files.append(main_js_path)
                    rc = requirejs_config.format(
                        bkey=resource,
                        paths=json.dumps(paths),
                        shims=json.dumps(shims),
                        name=main_js_path,
                        out=target_path + '/' + resource + '-compiled.js'
                    )
                    require_configs += rc
                    js_files.append(target_path + '/' + resource + '-compiled.js')
                    js_resources.append(resource)

            if res_obj.css:
                for css_file in res_obj.css:
                    css = portal.unrestrictedTraverse(css_file, None)
                    if css:
                        # We count how many folders to bundle to plone
                        elements = len(css_file.split('/'))
                        relative_paths = '../' * (elements - 1)

                        main_css_path = resource_to_dir(css)
                        target_dir = '/'.join(bundle.csscompilation.split('/')[:-1])  # noqa
                        target_name = bundle.csscompilation.split('/')[-1]
                        target_path = resource_to_dir(portal.unrestrictedTraverse(target_dir))  # noqa
                        less_file = "\"%s/%s\": \"%s\"" % (target_path, target_name, main_css_path)  # noqa
                        sourceMap_url = target_name + '.map'
                        less_files.append(less_file)
                        watch_files.append(main_css_path)
                        # replace urls

                        for webpath, direc in less_directories.items():
                            sed_config_final += sed_config.format(
                                path=target_path + '/' + target_name,
                                name='sed' + str(sed_count),
                                pattern=direc,
                                destination=relative_paths + webpath)
                            sed_count += 1

                        # replace the final missing paths
                        sed_config_final += sed_config.format(
                            path=target_path + '/' + target_name,
                            name='sed' + str(sed_count),
                            pattern=os.getcwd(),
                            destination='')
                        sed_count += 1

                    else:
                        print "No file found: " + script.js
        less_configs.append(less_config.format(
            name=bkey,
            globalVars=globalVars_string,
            files=',\n'.join(less_files),
            less_paths=json.dumps(less_paths),
            sourcemap_url=sourceMap_url,
            base_path=os.getcwd()))
        target_dir = '/'.join(bundle.jscompilation.split('/')[:-1])
        target_name = bundle.jscompilation.split('/')[-1]
        target_path = resource_to_dir(portal.unrestrictedTraverse(target_dir))
        uc = uglify_config.format(
            bkey=bkey,
            destination=target_path + '/' + target_name,
            files=json.dumps(js_files)
        )
        uglify_configs += uc

        requirejs_tasks = ''
        if js_resources:
            requirejs_tasks = ','.join(['"requirejs:' + r + '"' for r in js_resources]) + ','
        bundle_grunt_tasks += (
            "\ngrunt.registerTask('compile-%s',"
            "[%s 'less:%s', 'sed', 'uglify:%s']);"
        ) % (bkey, requirejs_tasks, bkey, bkey)


gruntfile = open('Gruntfile.js', 'w')
gruntfile.write(gruntfile_template.format(
    less=','.join(less_configs),
    requirejs=require_configs,
    uglify=uglify_configs,
    sed=sed_config_final,
    files=json.dumps(watch_files),
    bundleTasks=bundle_grunt_tasks)
)
gruntfile.close()
