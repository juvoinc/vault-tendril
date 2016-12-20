# tendril

## Overview

Tendril is a command line utility that facilitates the storage and retrieval
of versioned configuration files. Under the hood it uses Hashicorp's
[Vault](https://vaultproject.io).

At Juvo, we use it to store the configurations for all of our applications,
as well as storing [Terraform](https://terraform.io) state files and secret
files.

## Example usage

```
$ tendril read dev/webapp
export db_user="dev-webapp"
export db_host="10.1.2.3"
export db_port="5432"
export db_pass="luggage12345"
```

In this example we are showing the current configuration for the `webapp` application in
the `dev` environment. Note that the output is formatted so that it can directly
be sourced as environment variables without further manipulation. If a different
format is desired, you can specify either `--format=json` or `--format=yaml`. We
use JSON to expose configurations to [Ansible](https://www.ansible.com/) for use
as Ansible variables.

## Quick Start

### Prerequisites

* Python with virtualenv
* [Vault](https://www.vaultproject.io/downloads.html) in your `$PATH`

### Installation

```
git clone git@github.com:juvoinc/vault-tendril.git
cd vault-tendril
# Skip the next two virtualenv lines if you want global installation
virtualenv dev
. dev/bin/activate
python setup.py install
```

### Proper Installation

### Start the Vault Daemon

**Note**: This is **not** how you should run Vault in production!
This method is only for demonstration purposes so that you can play with
tendril.

`./scripts/start_daemons.sh`

When you are finished, you can clean things up with

`./scripts/stop_daemons.sh`

## Commands

### write

Valid ways to write a JSON or YAML file to vault via tendril:

`echo '{"key":"value"}' | tendril write PATH`

`tendril write --file FILE PATH`

### list

When you save data to a PATH, tendril adds in a version to the path so that you
can preserve history. The "list" command shows the next level of the path
specified, or the versions available.

```
$ echo '{"key":"value"}' | tendril write foo/bar
$ echo '{"key":"value2"}' | tendril write foo/baz
$ echo '{"key":"value3"}' | tendril write foo/baz
$ tendril list
foo/
$ tendril list foo
foo/bar/
foo/baz/
$ tendril list foo/baz
1
2
```
### promote

When a version of a config is promoted, it is then returned when a path without
a version is requested. It is also marked as current when running the list
command.

```
$ tendril promote foo/baz/2
$ tendril list foo/baz
1
2 (current)
```

### read

If a path is specified with a version, that version of the config will be shown.
If it is specified without a version and has a version promoted, that version
will be shown (even if it is not the most recent version). A desired format
may be specified. The default is to show the key/value pairs in export format,
ready for sourcing as environment variables, but JSON or YAML may be specified.

```
$ tendril read foo/baz/1
export key="value2"
$ tendril --format yaml read foo/baz # Note that version 2 has been promoted
---
key: value3
```

## Configuration

Tendril is configured via [INI files](https://en.wikipedia.org/wiki/INI_file).
Intelligent defaults have been set, but at the very least you will need to add
your vault token for production use. For demonstration and testing purposes, no
configuration file needs to be created.

By default, tendril reads configuration files from `/etc/tendril.conf`,
`~/.tendril`, and `./.tendril`, with the last taking highest precedence. If
multiple files exist, they will all be loaded. If you specify your own
configuration file, only the specified file will be read.

There is an example configuration file in `.tendril.example`.

## testing

There is a Makefile to make testing easy. To run tests without needing to have
vault running, run `make test`. To run the primitive tests with vault, run
`make test_primitives`. This assumes you have vault in your `$PATH` and will
start and stop vault automatically. If you are interested in contributing
patches back to the project, make sure the code pylints properly. You can
run pylint via `make pylint`.
