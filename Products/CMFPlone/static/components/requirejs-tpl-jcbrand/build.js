// See https://github.com/jrburke/r.js/blob/master/build/example.build.js
({
    // Assume your scripts are in a subdirectory under this path.
    appDir: 'example',

    // By default, all modules are located relative to this path.
    baseUrl: 'scripts',

    // Location of the runtime config be read for the build.
    mainConfigFile: 'example/scripts/main.js',

    //The directory path to save the output.
    dir: 'example-build',

    // If you do not want uglifyjs optimization.
    optimize: 'none',

    // Inlines any text! dependencies, to avoid separate requests.
    inlineText: true,

    // Modules to stub out in the optimized file.
    stubModules: ['underscore', 'text', 'tpl'],

    // Files combined into a build layer will be removed from the output folder.
    removeCombined: true,

    // This option will turn off the auto-preservation.
    preserveLicenseComments: false,

    //List the modules that will be optimized.
    modules: [
        {
            name: "main" // main config file
        }
    ]
})
