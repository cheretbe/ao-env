import invoke

def run_docker_test(context, image):
    print(f"Docker base image: {image}")
    with context.cd(".."):
        context.run(
            f"docker build . --build-arg base_image={image} --tag test-image:1.0 -f tests/docker/Dockerfile"
        )
    context.run("docker run --rm --name test test-image:1.0 /ao-env/install.py")
    # context.run("docker run --rm --name test test-image:1.0 /bin/sh -c 'ls -lha'")

@invoke.task(default=True)
def help(context):
    """This help message"""
    context.run('invoke --list')

@invoke.task
def test_ubuntu_bionic(context):
    """Run tests on Ubuntu 18.04"""
    run_docker_test(context, "ubuntu:18.04")

@invoke.task(test_ubuntu_bionic)
def test(context):
    """Run all tests"""