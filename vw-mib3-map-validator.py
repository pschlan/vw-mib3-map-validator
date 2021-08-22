# Simple VW MIB3 map update package validator
#
# (c) 2021 Patrick Schlangen <patrick@schlangen.me>
# Licensed under the terms of the MIT license.
#

import base64
import click
import json
import os
import sys
import hashlib


class MapValidationException(Exception):
    pass


class MapValidator:
    def __init__(self, root_path):
        self.root_path = root_path

    def validate(self):
        try:
            packages = self._parse_packages()
        except Exception as e:
            raise MapValidationException(f'Failed to parse PACKAGE.SLIST!', e)

        for package in packages:
            try:
                self._validate_package(package)
            except Exception as e:
                raise MapValidationException(f'Failed to validate package {package["id"]}!', e)

    def _parse_packages(self):
        package_slist_path = os.path.join(self.root_path, 'PACKAGE.SLIST')

        if not os.path.exists(package_slist_path):
            raise MapValidationException('PACKAGE.SLIST not found in root folder!')

        with open(package_slist_path, 'r') as f:
            packages_slist = json.load(f)
            payload_encoded = packages_slist['payload']
            payload_json = base64.b64decode(payload_encoded + '==')
            payload = json.loads(payload_json)
            packages = payload['packages']
            return packages

    def _validate_package(self, package):
        print(f'    Validating package: {package["id"]}')
        path = os.path.join(self.root_path, package['path'])
        if not os.path.exists(path):
            raise MapValidationException(f'Referenced package config not found: {package["path"]}')

        sha256_should = package['sha256'].lower()
        sha256_is = MapValidator._compute_file_sha256(path).lower()

        if sha256_should != sha256_is:
            raise MapValidationException(f'Checksum error in package config {package["path"]}: should = {sha256_should}, is = {sha256_is}')

        with open(path, 'r') as f:
            try:
                package_config = json.load(f)
            except Exception as e:
                raise MapValidationException(f'Failed to parse package config: {e}')

            if package['id'] != package_config['id']:
                raise MapValidationException(
                    f'Package id does not match in slist/package.cfg: f{package["id"]} != f{package_config["id"]}')

            if package['path'] != package_config['config_path']:
                raise MapValidationException(
                    f'Package path does not match in slist/package.cfg: f{package["path"]} != f{package_config["config_path"]}')

            package_data = package_config['data']
            if 'catalogs' in package_data:
                for catalog in package_data['catalogs']:
                    for layer in catalog['layers']:
                        for partition in layer['partitions']:
                            partition_path = os.path.join(self.root_path, partition['path'])
                            if not os.path.exists(partition_path):
                                raise MapValidationException(
                                    f'Referenced package catalog layer partition file not found: {partition["path"]}')

                            sha256_should = partition['sha256'].lower()
                            sha256_is = MapValidator._compute_file_sha256(partition_path).lower()

                            if sha256_should != sha256_is:
                                raise MapValidationException(
                                    f'Checksum error in catalog layer partition file {partition["path"]}: should = {sha256_should}, is = {sha256_is}')

    @staticmethod
    def _compute_file_sha256(filename):
        sha256 = hashlib.sha256()
        with open(filename, 'rb') as f:
            for block in iter(lambda: f.read(4096), b''):
                sha256.update(block)
        return sha256.hexdigest()


@click.command()
@click.option('--folder',
    help='Map folder (USB stick root or extracted tar file)',
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=False, readable=True))
def validate(folder):
    validator = MapValidator(folder)
    try:
        validator.validate()
        click.echo(click.style('Validation succeeded!', fg='green'))
        click.echo('This looks like a valid map update. Go ahead and try it in your vehicle!')
        sys.exit(0)
    except Exception as e:
        click.echo(click.style('Validation failed!', fg='red'))
        click.echo('This does not look like a valid map update:')
        click.echo(f'  {e}')
        sys.exit(1)


if __name__ == '__main__':
    validate()
