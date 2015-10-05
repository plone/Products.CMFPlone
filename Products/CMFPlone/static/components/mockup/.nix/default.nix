{ mockup ? { outPath = ./.; name = "mockup"; }
}:
let
  pkgs = import <nixpkgs> {};
  bowerPackages = import ./bower.nix { };
  nodePackages = import <nixpkgs/pkgs/top-level/node-packages.nix> {
    inherit pkgs;
    inherit (pkgs) stdenv nodejs fetchurl fetchgit;
    neededNatives = [ pkgs.python ] ++ pkgs.lib.optional pkgs.stdenv.isLinux pkgs.utillinux;
    self = nodePackages;
    generated = ./package.nix;
  };
in rec {
  tarball = pkgs.runCommand "mockup-1.6.0.tgz" { buildInputs = [ pkgs.nodejs ]; } ''
    mv `HOME=$PWD npm pack ${mockup}` $out
  '';
  build = nodePackages.buildNodePackage {
    name = "mockup-1.6.0";
    src = [ tarball ];
    buildInputs = [ ];
    deps = with nodePackages; [
      bower
      coveralls
      extend
      grunt
      grunt-cli
      grunt-contrib-copy
      grunt-contrib-jshint
      grunt-contrib-less
      grunt-contrib-requirejs
      grunt-contrib-uglify
      grunt-jscs-checker
      grunt-karma
      grunt-sed
      karma
      karma-chrome-launcher
      karma-coverage
      karma-junit-reporter
      karma-mocha
      karma-phantomjs-launcher
      karma-requirejs
      karma-sauce-launcher
      karma-script-launcher
      lcov-result-merger
      mocha
      requirejs
    ];
    postInstall = ''
      mkdir -p $out/bower_components
      ${pkgs.lib.concatStrings (map (p: ''
        ln -s ${pkgs.fetchbower p.name p.version p.target p.outputHash}/packages/*/${p.version} $out/bower_components/${p.name}
      '') bowerPackages )}
    '';

    peerDependencies = [];
    passthru.names = [ "mockup" ];
  };
}
