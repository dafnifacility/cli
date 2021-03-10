
import click
import time
import os
import modules.jwt_functions as jwt

from click.decorators import confirmation_option


@click.group()
@click.version_option(version='fake v0.0')
def dafnicmd():
    pass


@dafnicmd.command()
@click.option('--email', prompt=True, help="DAFNI email address")
@click.option('--password', prompt=True, hide_input=True)
def login(email: str, password: str):
    print('attempting login')
    users_jwt = jwt.get_dafni_jwt(email, password)


@dafnicmd.group()
def models():
    pass


@models.command()


@models.command(help="upload a docker image")
@click.option("--docker-image-tag")
@click.option("--metadata-file", default="model-metadata.yaml")
def upload(docker_image_tag: str, metadata_file: str):
    pass


@models.command()
@click.option("--model-id", )
def delete(model_id: str):
    pass


@dafnicmd.group()
def dataset():
    pass


@dataset.command()
@click.argument('path')
def create(path: str):
    if os.path.exists(path):
        print(f'path already exists: {path}')
    else:
        os.mkdir(path)
        with open(os.path.join(path, 'metadata.yaml'), 'w') as mdfile:
            print("metadata_title: whatever", file=mdfile)

    print(f'initialized new dataset in {path}')
    print('edit metadata.yaml and then run "dafni dataset upload" to continue')
    pass


@dataset.command()
@click.argument('path', default=".")
def upload(path: str):
    if not os.path.exists(os.path.join(path, 'metadata.yaml')):
        print('provide path to a directory containing metadata.yml')
    print('attempting to upload dataset')
    with click.progressbar(length=30) as bar:
        for i in range(bar.length):
            bar.update(1)
            time.sleep(0.1)
    print('upload complete - committing dataset')
    time.sleep(1)
    print('all done - dataset ID is: 7b443da6-57e5-415e-a281-9ea82a65c6b6')


@dataset.command()
@click.argument('path', default=".")
def validate(path: str):
    pass

@dataset.command()
@click.option('--dataset-id', prompt=True)
@click.argument('destination', default=".")
def download(dataset_id: str):
    pass


if __name__ == "__main__":
    dafnicmd()
