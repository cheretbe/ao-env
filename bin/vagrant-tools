#!/usr/bin/env python3

# pylint: disable=C0111,C0103

import sys
import os
import types
import enum
import textwrap
import subprocess
import pathlib
import shutil

from asciimatics.widgets import Frame, Layout, Label, Divider, Text, CheckBox, \
    RadioButtons, Button, DropdownList, PopUpDialog, Background
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.event import KeyboardEvent
from asciimatics.exceptions import ResizeScreenError, StopApplication


# pylint: disable=bad-whitespace
class FrameType(enum.Enum):
    FIRST   = enum.auto()
    REGULAR = enum.auto()
    LAST    = enum.auto()


VAGRANT_BOX_NAMES = [
    ("ubuntu/bionic64", 1),
    ("ubuntu/focal64",  2),
    ("ubuntu/xenial64", 3)
]
# pylint: enable=bad-whitespace


class WizardFrame(Frame):
    def __init__(self, screen, frame_type, frame_data):
        super(WizardFrame, self).__init__(
            screen,
            int(screen.height * 2 // 3),
            int(screen.width * 2 // 3),
            has_shadow=True,
            name="WizardFrame",
            title=frame_data.caption
        )
        self._layout = Layout([1, 18, 1], fill_frame=True)
        self.add_layout(self._layout)

        divider_layout = Layout([1])
        self.add_layout(divider_layout)
        divider_layout.add_widget(Divider(height=3), 0)

        self._buttons_layout = Layout([1, 1, 1, 1, 1])
        self.add_layout(self._buttons_layout)

        self._back_enabled = True
        if frame_type is FrameType.FIRST:
            self._back_enabled = False
            self._buttons_layout.add_widget(Button("Cancel", self._cancel_button_click), 3)
            self._buttons_layout.add_widget(Button("Next", self._next_button_click), 4)
        elif frame_type is FrameType.REGULAR:
            self._buttons_layout.add_widget(Button("Cancel", self._cancel_button_click), 2)
            self._buttons_layout.add_widget(Button("Back", self._back_button_click), 3)
            self._buttons_layout.add_widget(Button("Next", self._next_button_click), 4)
        elif frame_type is FrameType.LAST:
            self._buttons_layout.add_widget(Button("Cancel", self._cancel_button_click), 2)
            self._buttons_layout.add_widget(Button("Back", self._back_button_click), 3)
            self._buttons_layout.add_widget(Button("Finish", self._next_button_click), 4)

        self._frame_data = frame_data

    def _cancel_button_click(self):
        self._frame_data.cancelled = True
        raise StopApplication("Exit on Cancel button click")

    def _back_button_click(self):
        if self._back_enabled:
            self.save()
            self._frame_data.controls_data = self.data
            self._frame_data.forward = False
            raise StopApplication("Exit on Back button click")

    def _next_button_click(self):
        self.save()
        self._frame_data.controls_data = self.data
        self._frame_data.forward = True
        raise StopApplication("Exit on Next button click")

    def process_event(self, event):
        if isinstance(event, KeyboardEvent):
            if event.key_code == Screen.KEY_ESCAPE:
                self._cancel_button_click()
            elif event.key_code == Screen.ctrl("n"):
                self._next_button_click()
            elif event.key_code == Screen.ctrl("b"):
                self._back_button_click()
        return super(WizardFrame, self).process_event(event)


class CommonSettingsFrame(WizardFrame):
    def __init__(self, screen, frame_type, frame_data):
        super(CommonSettingsFrame, self).__init__(screen, frame_type, frame_data)

        self._layout.add_widget(Label("VM count:", height=2), 1)
        self._layout.add_widget(
            RadioButtons(
                [("Single VM", 1), ("2 VMs", 2), ("3 VMs", 3)],
                name="vm_count"
            ),
            1
        )

        self._layout.add_widget(Divider(height=1, draw_line=False), 1)
        self._layout.add_widget(Label("Additional options:", height=2), 1)

        self._layout.add_widget(
            CheckBox("Add local YAML config", name="add_config"),
            1
        )
        self._layout.add_widget(Divider(height=1, draw_line=False), 1)

        self._layout.add_widget(
            CheckBox(
                "Require 'vagrant-vbguest' plugin",
                name="require_vagrant_vbguest"
            ),
            1
        )
        self._layout.add_widget(Divider(height=1, draw_line=False), 1)

        self._add_intnet_checkbox = CheckBox(
            "Add VirtualBox internal network",
            name="add_vb_intnet",
            on_change=self._on_add_intnet_change
        )
        self._layout.add_widget(self._add_intnet_checkbox, 1)
        self._intnet_name_edit = Text(
            # label="Network name:",
            name="intnet_name"
        )
        # self._intnet_name_edit.offset = 5
        self._layout.add_widget(self._intnet_name_edit, 1)
        # self._layout.add_widget(Divider(height=1, draw_line=False), 1)

        self.data = frame_data.controls_data
        self.fix()

    def _on_add_intnet_change(self):
        self._intnet_name_edit.disabled = not self._add_intnet_checkbox.value


class EditFrame(WizardFrame):
    def __init__(self, screen, frame_type, frame_data):
        super(EditFrame, self).__init__(screen, frame_type, frame_data)

        self._layout.add_widget(Divider(height=1, draw_line=False), 1)
        self._vm_name_edit = Text(
            label="VM name:",
            name="vm_name"
        )
        self._vm_name_edit.disabled = not frame_data.multi_vm
        self._layout.add_widget(self._vm_name_edit, 1)

        self._layout.add_widget(
            DropdownList(VAGRANT_BOX_NAMES, label="Box name:", name="box_name"),
            1
        )

        self._layout.add_widget(Divider(height=1, draw_line=False), 1)
        self._layout.add_widget(
            Text(label="CPU count:", name="cpu_count", max_length=2, validator="^[0-9]*$"),
            1
        )
        self._layout.add_widget(
            Text(label="Memory (GiB):", name="memory", max_length=3, validator="^[0-9]*$"),
            1
        )

        self._enable_vbguest_checkbox = CheckBox("'vbguest' auto-update", name="enable_vbguest")
        self._layout.add_widget(self._enable_vbguest_checkbox, 1)
        self._enable_vbguest_checkbox.disabled = not frame_data.vbguest_plugin_is_present

        self._layout.add_widget(
            CheckBox("Add inline shell provision", name="inline_shell_provision"),
            1
        )
        self._layout.add_widget(
            CheckBox("Add shell provision script", name="shell_provisioner"),
            1
        )
        self._layout.add_widget(
            CheckBox("Add Ansible provision playbook", name="ansible_provisioner"),
            1
        )
        self._layout.add_widget(
            CheckBox("Disable /vagrant shared folder", name="disable_vagrant_share"),
            1
        )
        self._layout.add_widget(
            CheckBox("Add port mapping 8080:80", name="port_mapping"),
            1
        )
        self._disable_autostart_checkbox = CheckBox(
            "Disable autostart", name="disable_autostart"
        )
        self._layout.add_widget(self._disable_autostart_checkbox, 1)
        self._disable_autostart_checkbox.disabled = not frame_data.multi_vm

        self._layout.add_widget(Divider(height=1, draw_line=False), 1)
        self._add_extra_drive_checkbox = CheckBox(
            "Add extra virtual HDD",
            name="add_extra_hdd",
            on_change=self._on_add_extra_drive_change
        )
        self._layout.add_widget(self._add_extra_drive_checkbox, 1)
        self._extra_drive_name_edit = Text(
            label="File name:",
            name="extra_drive_file_name"
        )
        self._layout.add_widget(self._extra_drive_name_edit, 1)
        self._extra_drive_size_edit = Text(
            label="Size (GiB):",
            name="extra_drive_size",
            validator="^[0-9]*$"
        )
        self._layout.add_widget(self._extra_drive_size_edit, 1)

        self._layout.add_widget(Divider(height=1, draw_line=False), 1)
        self._ip_address_edit = Text(
            label="IP address:",
            name="ip_address"
        )
        self._layout.add_widget(self._ip_address_edit, 1)
        self._ip_address_edit.disabled = not frame_data.intnet_is_present

        self.data = frame_data.controls_data
        self.fix()

    def _on_add_extra_drive_change(self):
        self._extra_drive_name_edit.disabled = not self._add_extra_drive_checkbox.value
        self._extra_drive_size_edit.disabled = not self._add_extra_drive_checkbox.value


class FinishFrame(WizardFrame):
    def __init__(self, screen, frame_type, frame_data):
        super(FinishFrame, self).__init__(screen, frame_type, frame_data)

        self._layout.add_widget(Divider(height=5, draw_line=False), 1)
        self._layout.add_widget(
            Label("Select 'Finish' to write a Vagrantfile,"), 1
        )
        self._layout.add_widget(
            Label("based on selected options"), 1
        )

        self.fix()
        self.switch_focus(self._buttons_layout, 4, 0)

    def process_event(self, event):
        if isinstance(event, KeyboardEvent):
            if event.key_code == ord("q"):
                # import ipdb
                # ipdb.set_trace()
                self.switch_focus(self._buttons_layout, 4, 0)
        return super(FinishFrame, self).process_event(event)


def run_frame(frame_type, frame_data):
    last_scene = None
    while True:
        try:
            Screen.wrapper(
                run_frame_callback,
                catch_interrupt=False,
                arguments=[last_scene, frame_type, frame_data]
            )
            break
        except ResizeScreenError as err:
            last_scene = err.scene
    if frame_data.cancelled:
        sys.exit("Cancelled by user")


def run_frame_callback(screen, scene, frame_type, frame_data):
    if frame_type is FrameType.FIRST:
        main_frame = CommonSettingsFrame(screen, frame_type, frame_data)
    elif frame_type is FrameType.REGULAR:
        main_frame = EditFrame(screen, frame_type, frame_data)
    elif frame_type is FrameType.LAST:
        main_frame = FinishFrame(screen, frame_type, frame_data)
    scenes = [
        Scene(
            [
                Background(screen),
                main_frame
            ],
            -1
        )
    ]
    screen.play(scenes, stop_on_resize=True, start_scene=scene, allow_int=True)


def new_wizard_step(state, data=None):
    if data is None:
        data = {}
    return types.SimpleNamespace(
        state=state,
        controls_data=data,
        cancelled=False,
        forward=False
    )


def set_edit_step_data(vm_index, data):
    if data.multi_vm:
        if data.controls_data.get("vm_name") in [None, "", "default"]:
            data.controls_data["vm_name"] = "host" + str(vm_index + 1)
    else:
        data.controls_data["vm_name"] = "default"
        data.controls_data["disable_autostart"] = False

    if not data.vbguest_plugin_is_present:
        data.controls_data["enable_vbguest"] = False

    if data.intnet_is_present:
        if data.controls_data.get("ip_address") in [None, ""]:
            data.controls_data["ip_address"] = "172.24.0.{}".format(10 + vm_index)
    else:
        data.controls_data["ip_address"] = ""

def get_template_file(file_name):
    return pathlib.Path(__file__).resolve().parent.parent / \
        "templates" / file_name


def backup_current_vagrantfile():
    if os.path.isfile("Vagrantfile"):
        counter = 1
        while os.path.isfile(f"Vagrantfile.{counter}"):
            counter += 1
        print(f"Saving backup copy of existing Vagrantfile as Vagrantfile.{counter}")
        os.rename("Vagrantfile", f"Vagrantfile.{counter}")


# pylint: disable=too-many-locals,too-many-branches,too-many-statements
def write_vagrantfile(v_file, steps):
    multi_vm = steps[0].controls_data["vm_count"] > 1
    if steps[0].controls_data["add_vb_intnet"]:
        intnet_name = steps[0].controls_data["intnet_name"]
    else:
        intnet_name = ""

    if steps[0].controls_data["require_vagrant_vbguest"]:
        # pylint: disable=line-too-long
        plugins_code = textwrap.dedent(
            """
                required_plugins = %w(vagrant-vbguest)

                plugins_to_install = required_plugins.select { |plugin| not Vagrant.has_plugin? plugin }
                if not plugins_to_install.empty?
                  puts "This Vagrantfile needs one or more additional plugins to be installed: #{plugins_to_install.join(', ')}"
                  puts "Use the following command:\\n\\n"
                  puts "vagrant plugin install #{plugins_to_install.join(' ')}\\n\\n"
                  abort "Installation of one or more additional plugins needed. Aborting."
                end

            """)
        # pylint: enable=line-too-long
        v_file.write(plugins_code)

    if steps[0].controls_data["add_config"]:
        config_code = textwrap.dedent(
            """
                # vm_memory = "4096"
                # vm_cpus = "1"
                if File.file?("local-config.yml")
                  local_config = YAML.load_file("local-config.yml")
                  unless local_config.nil?
                    # vm_memory = local_config.fetch("vm_memory", vm_memory)
                    # vm_cpus = local_config.fetch("vm_cpus", vm_cpus)
                  end
                end

            """)
        v_file.write(config_code)
        if not os.path.isfile("local-config.yml"):
            with open("local-config.yml", "w") as f:
                f.write("---\n")
                f.write("# vm_memory: \"2048\"\n")
                f.write("# vm_cpus: \"2\"\n")
        # pylint: disable=subprocess-run-check
        proc = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if proc.returncode == 0:
            need_gitignore_update = True
            if os.path.isfile(".gitignore"):
                with open(".gitignore", "r") as f:
                    need_gitignore_update = not any("local-config.yml" in line for line in f)
            if need_gitignore_update:
                with open(".gitignore", "a+") as f:
                    f.write("local-config.yml\n")

    extra_hdds = []
    for step in wizard_steps:
        if step.state == "edit":
            if step.controls_data["add_extra_hdd"]:
                extra_hdds += [
                    '  {{"vm_name" => :"{vm_name}", '
                    '"hdd_name" => "{file_name}", '
                    '"hdd_size" => {file_size}}}'.format(
                        vm_name=step.controls_data["vm_name"],
                        file_name=step.controls_data["extra_drive_file_name"],
                        file_size=int(step.controls_data["extra_drive_size"]) * 1024
                    )
                ]
    if len(extra_hdds) > 0:
        v_file.write("$hdd_info = [\n")
        v_file.write(",\n".join(extra_hdds) + "\n")
        v_file.write("]\n\n")

        with get_template_file("vagrantfile_attach_disk.rb").open("r") as f:
            v_file.write(f.read())
        v_file.write("\n")

    v_file.write("Vagrant.configure(\"2\") do |config|\n")
    first_vm = True

    for step in wizard_steps:
        if step.state == "edit":
            if multi_vm:
                vm_name = step.controls_data["vm_name"]
                config_var = vm_name.replace("-", "_")
                if first_vm:
                    first_vm = False
                else:
                    v_file.write("\n")
                if step.controls_data["disable_autostart"]:
                    autostart = ", autostart: false"
                else:
                    autostart = ""
                v_file.write(f"  config.vm.define :\"{vm_name}\"{autostart} do |{config_var}|\n")
                padding = "    "
            else:
                padding = "  "
                config_var = "config"

            box_name = ""
            for vagrant_box_name in VAGRANT_BOX_NAMES:
                if vagrant_box_name[1] == step.controls_data["box_name"]:
                    box_name = vagrant_box_name[0]
                    break
            v_file.write(
                "{padding}{config}.vm.box = \"{box}\"\n".format(
                    padding=padding,
                    config=config_var,
                    box=box_name
                )
            )
            if multi_vm:
                v_file.write(f'{padding}{config_var}.vm.hostname = "{vm_name}"\n')

            v_file.write(f'{padding}{config_var}.vm.provider "virtualbox" do |vb|\n')
            if steps[0].controls_data["add_config"]:
                v_file.write(f"{padding}  # vb.memory = vm_memory\n")
                v_file.write(f"{padding}  # vb.cpus = vm_cpus\n")
            vm_memory = step.controls_data["memory"]
            if vm_memory != "":
                vm_memory = str(int(vm_memory) * 1024)
                v_file.write(f"{padding}  vb.memory = {vm_memory}\n")
            vm_cpus = step.controls_data["cpu_count"]
            if vm_cpus != "":
                v_file.write(f"{padding}  vb.cpus = {vm_cpus}\n")
            v_file.write(f'{padding}  vb.customize ["modifyvm", :id, "--groups", "/__vagrant"]\n')

            if box_name.startswith("ubuntu/"):
                v_file.write(
                    f'{padding}  vb.customize ["modifyvm", :id, "--uartmode1", "disconnected"]\n'
                )

            v_file.write(f"{padding}end\n")

            if step.controls_data["enable_vbguest"]:
                v_file.write(f"{padding}{config_var}.vbguest.auto_update = true\n")

            if step.controls_data["disable_vagrant_share"]:
                v_file.write(
                    f'{padding}{config_var}.vm.synced_folder ".", "/vagrant", disabled: true\n'
                )

            if step.controls_data["port_mapping"]:
                v_file.write(
                    f'{padding}{config_var}.vm.network "forwarded_port", guest: 80, host: 8080\n'
                )

            if intnet_name != "":
                ip_address = step.controls_data["ip_address"]
                v_file.write(
                    f'{padding}{config_var}.vm.network "private_network", '
                    f'ip: "{ip_address}", virtualbox__intnet: "{intnet_name}"\n'
                )

            if step.controls_data["inline_shell_provision"]:
                v_file.write(f'{padding}{config_var}.vm.provision "shell", '
                    'name: "Provision template",\n')
                v_file.write(f'{padding}  keep_color: true, # privileged: false,\n')
                v_file.write(f'{padding}  inline: <<-SHELL\n')
                v_file.write(f'{padding}    set -euo pipefail\n')
                v_file.write(f'{padding}    uname -a\n')
                v_file.write(f'{padding}  SHELL\n')

            if step.controls_data["shell_provisioner"]:
                os.makedirs("provision", exist_ok=True)
                script_name = f"{vm_name}_provision.sh" if multi_vm else "provision.sh"
                if not os.path.isfile(f"./provision/{script_name}"):
                    shutil.copyfile(
                        str(get_template_file("vagrant_provision.sh")),
                        f"./provision/{script_name}")
                v_file.write("\n")
                v_file.write(f'{padding}{config_var}.vm.provision "shell", '
                    f'name: "Provision shell script",\n{padding}  '
                    f'keep_color: true, path: "provision/{script_name}"\n')

            if step.controls_data["ansible_provisioner"]:
                os.makedirs("provision", exist_ok=True)
                playbook_name = f"{vm_name}_provision.yml" if multi_vm else "provision.yml"
                if not os.path.isfile(f"./provision/{playbook_name}"):
                    shutil.copyfile(
                        str(get_template_file("vagrant_provision.yml")),
                        f"./provision/{playbook_name}")
                v_file.write("\n")
                v_file.write(f'{padding}{config_var}.vm.provision "ansible_local" do |ansible|\n')
                v_file.write(f'{padding}  ansible.playbook = "provision/{playbook_name}"\n')
                v_file.write(f'{padding}  ansible.compatibility_mode = "2.0"\n')
                v_file.write(f'{padding}  ansible.extra_vars = {{\n')
                v_file.write(f'{padding}    "ansible_python_interpreter": "/usr/bin/python3"\n')
                v_file.write(f'{padding}  }}\n')
                v_file.write(f'{padding}end\n')

            if multi_vm:
                v_file.write("  end\n")
    v_file.write("end\n")


wizard_steps = [
    new_wizard_step("init", {"intnet_name": "vagrant-intnet"})
]
wizard_steps[0].caption = "Create custom Vagrantfile"
wizard_idx = 0
# pylint: enable=too-many-locals,too-many-branches,too-many-statements

while True:
    c_step = wizard_steps[wizard_idx]
    if c_step.state == "init":
        run_frame(FrameType.FIRST, c_step)

        old_edit_steps = [step for step in wizard_steps if step.state == "edit"]
        del wizard_steps[1:]

        vm_count = c_step.controls_data["vm_count"]
        for i in range(0, vm_count):
            if len(old_edit_steps) > i:
                edit_step = old_edit_steps[i]
            else:
                edit_step = new_wizard_step(
                    "edit",
                    {
                        "extra_drive_file_name": "extra_drive.vdi",
                        "extra_drive_size": "10"
                    }
                )
            edit_step.multi_vm = vm_count > 1
            if edit_step.multi_vm:
                edit_step.caption = f"VM {i + 1} of {vm_count}"
            else:
                edit_step.caption = "Default VM"
            edit_step.vbguest_plugin_is_present = c_step.controls_data["require_vagrant_vbguest"]
            edit_step.intnet_is_present = c_step.controls_data["add_vb_intnet"]
            edit_step.intnet_name = c_step.controls_data["intnet_name"]
            set_edit_step_data(i, edit_step)
            # print(edit_step)
            wizard_steps += [edit_step]

        wizard_steps += [new_wizard_step("finish")]
        wizard_steps[-1].caption = "Write Vagrantfile"
        wizard_idx += 1
    elif c_step.state == "edit":
        run_frame(FrameType.REGULAR, c_step)
        if c_step.forward:
            wizard_idx += 1
        else:
            wizard_idx -= 1
    elif c_step.state == "finish":
        run_frame(FrameType.LAST, c_step)
        if c_step.forward:
            # write_vagrantfile(sys.stdout, wizard_steps)
            backup_current_vagrantfile()
            with open("Vagrantfile", "w") as f:
                write_vagrantfile(f, wizard_steps)
            break
        wizard_idx -= 1
