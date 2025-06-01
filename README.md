# pdm-audit

PDM Audit is an auditing tool inspired by commands like `npm audit`. It primarily relies on the ability of PDM to export the current lock file as `requirements.txt` and the ability of `pip-audit` to use these files for an audit against various CVE registries.

## Usage

You can add `pdm-audit` in two different flavors.

### Global Environment

You can use the same environment PDM is installed in just by running

```shell
$ pdm self add pdm-audit
```

This will add `pdm-audit` to your global environment and make it available in every project, unless it is locally disabled.

### Project local installation

Each project may introduce a local setting called  `tools
.pdm.plugins` which will be installed locally by running `pdm install --plugins`. To achieve this, you must add the following lines to your local `pyproject.toml`:

```toml

[tool.pdm]
plugins = ["pdm-audit"]
```

## Invocation and Usage

Unless opted out, pdm-audit will run as a post-install hook. This means, that every time a package is added, removed, updated or installed, the auditing will take place.

It will export the currentbstate of the lock file to requirements.txt and run the auditor against it.

It is also possible to run an explicit audit by invoking the `pdm audit` command.

### Command-line options

**TODO**

### Configuration options

**TODO**

## Contributions

**TODO**
