# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"
VBOXNAME = "mockup"
VBOXRAM = 2048

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.ssh.forward_agent = true
  config.vm.box = "ubuntu/trusty64"

  if Vagrant.has_plugin?("vagrant-vbguest")
    config.vbguest.auto_update = false
    config.vbguest.installer = VagrantVbguest::Installers::Ubuntu
  end

  config.vm.define "virtualbox" do |virtualbox|
    virtualbox.vm.network :private_network, ip: "10.0.1.2"
    virtualbox.vm.network :public_network, ip: "172.16.1.3"

    virtualbox.vm.network "forwarded_port", guest: 8000, host: 8000

    virtualbox.vm.provision :shell,
    :inline => "(grep -q -E '^mesg n$' /root/.profile && " \
               "sed -i 's/^mesg n$/tty -s \\&\\& mesg n/g' /root/.profile && " \
               "echo 'Ignore the previous error about stdin not being a tty. Fixing it now...') || exit 0;"

    virtualbox.vm.provision :shell, :path => "provision.sh", :args=>VBOXNAME

    config.vm.synced_folder ".", "/vagrant"

    # if Vagrant.has_plugin?("vagrant-cachier")
        # config.cache.scope = :box
        # config.cache.enable :apt_lists
        # config.cache.enable :apt
        # config.cache.enable :npm
    # end
  end

  config.vm.provider "virtualbox" do |vb|
    vb.memory = VBOXRAM
  end


  if Vagrant.has_plugin?("vagrant-triggers")
    config.trigger.after :destroy do
        # delete node leftovers
        run "rm -rf node_modules"
    end
  end

end
