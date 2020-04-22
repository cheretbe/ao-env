class VagrantPlugins::ProviderVirtualBox::Action::SetName
  alias_method :original_call, :call
  def call(env)
    vm_hdd_info = $hdd_info.find { |entry| entry["vm_name"] == env[:machine].name }
    unless vm_hdd_info.nil?
      driver = env[:machine].provider.driver
      vm_uuid = driver.uuid
      vm_info = driver.execute("showvminfo", vm_uuid, "--machinereadable").split("\n")
      # We are looking for CfgFile parameter to unquote and extract path from it
      # CfgFile="/path/to/vm/vm_name.vbox" => /path/to/vm
      cfg_line = vm_info.find { |line| line.start_with?("CfgFile=") }
      vm_path = File.dirname(cfg_line.split("=", 2).last.gsub('"', ""))
      second_hdd_file = File.join(vm_path, vm_hdd_info["hdd_name"])
      unless File.exist?(second_hdd_file)
        env[:ui].detail("Creating virtual drive #{second_hdd_file}")
        driver.execute("createhd", "--filename", second_hdd_file,
          "--variant", "Standard", "--size", vm_hdd_info["hdd_size"].to_s)
      end
      env[:ui].detail("Attaching virtual drive #{second_hdd_file} to the VM")
      driver.execute("storageattach", vm_uuid, "--storagectl", "SCSI",
        "--port", "2", "--device", "0", "--type", "hdd",
        "--medium", second_hdd_file)
    end

    original_call(env)
  end
end
