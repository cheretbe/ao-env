"""Testinfra tests to ensure the installation was correct"""

def test_virtual_env(host):
    """Check if Python virtualenv was created"""
    assert host.file("/home/testuser/.cache/ao-env/virtualenv-py3/bin/activate").exists

def test_packages(host):
    """Selectively check if apt and pip packages were installed"""
    assert host.package("dialog").is_installed
    assert host.package("jq").is_installed

    pip_packages = host.pip_package.get_packages(
        pip_path="/home/testuser/.cache/ao-env/virtualenv-py3/bin/pip3"
    )
    assert "asciimatics" in pip_packages
    assert "PyInquirer" in pip_packages

def test_fonts(host):
    """Check if fonts symlink was created successfully"""
    assert host.file("/home/testuser/.local/share/fonts/ao-env").is_symlink
    assert host.file("/home/testuser/.local/share/fonts/ao-env/windows-ttf/arial.ttf").exists
