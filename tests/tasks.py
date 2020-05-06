#pylint: disable=missing-module-docstring,missing-function-docstring
#pylint: disable=import-error
import invoke
#pylint: enable=import-error
import colorama


colorama.init()


def run_docker_test(context, image):
    print(f"Docker base image: {image}")
    with context.cd(".."):
        context.run(
            f"docker build . --build-arg base_image={image} "
            "--tag test-image:1.0 -f tests/docker/Dockerfile"
        )
    try:
        # context.run("ls /aaa")
        context.run("docker run -dt --name test  test-image:1.0 /bin/sh")
        context.run(
            "docker exec test /home/testuser/.local/share/ao-env/install.sh"
        )
        context.run(
            "py.test --hosts='docker://test' -v installer_tests",
            pty=True
        )
    finally:
        print("Destroying test container")
        context.run("docker rm test --force")

    context.run("docker image prune --force")

@invoke.task(default=True)
def show_help(context):
    """This help message"""
    context.run('invoke --list')

@invoke.task
def unit_tests(context):
    """Run unit tests on local machine"""
    context.run("pytest -v unit_tests", pty=True)

@invoke.task
def test_ubuntu_bionic(context):
    """Run tests on Ubuntu 18.04 container"""
    run_docker_test(context, "ubuntu:18.04")

@invoke.task
def test_ubuntu_focal(context):
    """Run tests on Ubuntu 20.04 container"""
    run_docker_test(context, "ubuntu:20.04")

#pylint: disable=unused-argument
@invoke.task(unit_tests, test_ubuntu_bionic)
def test(context):
    """Run all tests"""
    print(colorama.Fore.GREEN + "All tests passed" + colorama.Style.RESET_ALL)
#pylint: enable=unused-argument

@invoke.task
def interactive(context):
    """Run interactive bash shell on a temporary Ubuntu 18.04 container"""
    with context.cd(".."):
        context.run(
            f"docker build . --build-arg base_image=ubuntu:18.04 "
            "--tag test-image:1.0 -f tests/docker/Dockerfile"
        )
    context.run(
        "docker run --rm  -ti -v /ao-env:/ao-env:ro --name test"
        " test-image:1.0 /bin/bash",
        pty=True
    )
