# -*- coding: utf-8 -*-
from plone.registry.interfaces import IRegistry
from plone.resource.directory import FilesystemResourceDirectory
from plone.resource.file import FilesystemFile
from plone.subrequest import subrequest
from Products import CMFPlone
from Products.CMFCore.FSFile import FSFile
from Products.CMFPlone.interfaces import IBundleRegistry
from Products.CMFPlone.interfaces import IResourceRegistry
from Products.Five.browser.resource import DirectoryResource
from Products.Five.browser.resource import FileResource
from zope.component import getUtility
from zope.site.hooks import setSite

import json
import os
import uuid

# some initial script setup
if 'SITE_ID' in os.environ:
    site_id = os.environ['SITE_ID']
else:
    site_id = 'Plone'
print('Using site id: {0}'.format(site_id))

compile_path = ''
if 'COMPILE_DIR' in os.environ:
    compile_path = os.environ['COMPILE_DIR']
print('Target compile path: {0}'.format(compile_path or 'fetch from bundles'))

portal = app[site_id]  # noqa
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
                files: [
                    {files}
                ],
                options: {{
                    compress: true,
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
                    paths: {less_paths},
                    modifyVars: {{
{globalVars}
                    }}
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
                        full_file_name = temp_resource_folder + \
                            '/' + file_name + file_type
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
        paths[requirejs + '-url'] = resource_to_dir(
            portal.unrestrictedTraverse(script.url)
        )


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
        t_object = portal.unrestrictedTraverse(
            str(t.replace('LOCAL/', '').replace('\\"', '')),
            None
        )
        if t_object:
            t_file = resource_to_dir(t_object)
            t_file = t_file.replace(os.getcwd() + '/', '')
            globalVars[name] = "'%s/'" % t_file
        else:
            print "No file found: " + \
                str(t.replace('LOCAL/', '').replace('\\"', ''))  #
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
            ld_key = css.rsplit('/', 1)[0]
            less_directories[ld_key] = local_file.rsplit('/', 1)[0].replace(
                os.getcwd() + '/',
                ''
            )
            # local_file = local_file.replace(os.getcwd(), '')
            # relative = ''
            # for i in range(len(local_file.split('/'))):
            #     relative += '../'
            # globalVars[name.replace('.', '_')] = "'%s'" % local_file  # noqa
            globalVars[name.replace('.', '_')] = "'{0}'".format(
                local_file.split('/')[-1]
            )
            if '/'.join(local_file.split('/')[:-1]) not in less_paths:
                less_paths.append('/'.join(local_file.split('/')[:-1]))
        else:
            print "No file found: " + css

globalVars_string = ""
for key, value in sorted(globalVars.items()):
    globalVars_string += '{0}"{1}": "{2}",\n'.format(22*' ', key, value)


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
    css_target_path = css_target_name = ''
    js_target_path = js_target_name = ''

    if compile_path:
        target_name = bundle.__prefix__.split('/').pop()
        css_target_name = target_name + 'min.css'
        js_target_name = target_name + 'min.js'
        css_target_path = js_target_path = os.path.abspath(compile_path)
    else:
        print('"{0}" bundles compiles paths/filename'.format(bkey))
        if bundle.csscompilation:
            css_compilation = bundle.csscompilation.split('/')
            css_target_name = css_compilation[-1]
            css_target_path = resource_to_dir(portal.unrestrictedTraverse(
                '/'.join(css_compilation[:-1])))
            print('- css path: {0}'.format(css_target_path))
            print('- css name: {0}'.format(css_target_name))
        if bundle.jscompilation:
            js_compilation = bundle.jscompilation.split('/')
            js_target_name = js_compilation[-1]
            js_target_path = resource_to_dir(
                portal.unrestrictedTraverse(
                    '/'.join(js_compilation[:-1])
                )
            )
            print('- js path:  {0}'.format(js_target_path))
            print('- js name:  {0}'.format(js_target_name))
    if bundle.compile:
        less_files = {}
        js_files = []
        js_resources = []
        sed_task_ids = []
        for resource in bundle.resources:
            res_obj = resources[resource]
            if res_obj.js:
                js_object = portal.unrestrictedTraverse(res_obj.js, None)
                if js_object:
                    main_js_path = resource_to_dir(js_object)
                    target_path = resource_to_dir(
                        portal.unrestrictedTraverse(res_obj.js))
                    target_path = '/'.join(target_path.split('/')[:-1])
                    watch_files.append(main_js_path)
                    rjs_paths = paths.copy()
                    if bundle.stub_js_modules:
                        for stub in bundle.stub_js_modules:
                            rjs_paths[stub] = 'empty:'
                    rc = requirejs_config.format(
                        bkey=resource,
                        paths=json.dumps(rjs_paths),
                        shims=json.dumps(shims),
                        name=main_js_path,
                        out=target_path + '/' + resource + '-compiled.js'
                    )
                    require_configs += rc
                    js_files.append(target_path + '/' +
                                    resource + '-compiled.js')
                    js_resources.append(resource)

            if res_obj.css:
                if not css_target_path:
                    raise KeyError(
                        'Missing or empty <value key="csscompilation" /> '
                        'in {}'.format(bundle.__prefix__))

                for css_file in res_obj.css:
                    css = portal.unrestrictedTraverse(css_file, None)
                    if css:
                        # We count how many folders to bundle to plone
                        elements = len(css_file.split('/'))
                        relative_paths = '../' * (elements - 1)

                        main_css_path = resource_to_dir(css)
                        dest_path = '{}/{}'.format(
                            css_target_path, css_target_name)
                        less_files.setdefault(dest_path, [])
                        less_files[dest_path].append(main_css_path)
                        sourceMap_url = css_target_name + '.map'
                        watch_files.append(main_css_path)
                        # replace urls

                        for webpath, direc in less_directories.items():
                            sed_id = 'sed' + str(sed_count)
                            sed_task_ids.append("'sed:%s'" % sed_id)
                            sed_config_final += sed_config.format(
                                path=css_target_path + '/' + css_target_name,
                                name=sed_id,
                                pattern=direc,
                                destination=relative_paths + webpath)
                            sed_count += 1

                        # replace the final missing paths
                        sed_id = 'sed' + str(sed_count)
                        sed_task_ids.append("'sed:%s'" % sed_id)
                        sed_config_final += sed_config.format(
                            path=css_target_path + '/' + css_target_name,
                            name=sed_id,
                            pattern=os.getcwd(),
                            destination='')
                        sed_count += 1

                    else:
                        print "No file found: " + script.js

        if less_files:
            less_configs.append(less_config.format(
                name=bkey,
                globalVars=globalVars_string,
                files=json.dumps(less_files),
                less_paths=json.dumps(sorted(less_paths), indent=22),
                sourcemap_url=sourceMap_url,
                base_path=os.getcwd()))

        if js_files:
            if not js_target_path:
                raise KeyError(
                    'Missing or empty <value key="jscompilation" /> '
                    'in {}'.format(bundle.__prefix__))

            uc = uglify_config.format(
                bkey=bkey,
                destination=js_target_path + '/' + js_target_name,
                files=json.dumps(js_files)
            )
            uglify_configs += uc

        requirejs_tasks = ''
        if js_resources:
            requirejs_tasks = ','.join(
                ['"requirejs:' + r + '"' for r in js_resources]) + ','
        bundle_grunt_tasks += (
            "\ngrunt.registerTask('compile-%s',"
            "[%s 'less:%s', %s, 'uglify:%s']);"
        ) % (bkey, requirejs_tasks, bkey, ', '.join(sed_task_ids), bkey)


with open('Gruntfile.js', 'w') as gruntfile:
    gruntfile.write(
        gruntfile_template.format(
            less=','.join(less_configs),
            requirejs=require_configs,
            uglify=uglify_configs,
            sed=sed_config_final,
            files=json.dumps(watch_files),
            bundleTasks=bundle_grunt_tasks
        )
    )
