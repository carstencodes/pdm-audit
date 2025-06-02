# pdm-audit

PDM Audit is an auditing tool inspired by commands like `npm audit`. It primarily relies on the ability of `pdm` to export the current lock file as `requirements.txt` and the ability of `pip-audit` to use these files for an audit against various CVE registries.

## Usage

You can add `pdm-audit` in two different flavors.

### Global Environment

You can use the same environment PDM is installed in just by running

```shell
$ pdm self add pdm-audit
```

This will add `pdm-audit` to your global environment and make it available in every project, unless it is locally disabled.

### Project local installation

Each project may introduce a local setting called  `tool.pdm.plugins` which will be installed locally by running `pdm install --plugins`. To achieve this, you must add the following lines to your local `pyproject.toml`:

```toml

[tool.pdm]
plugins = ["pdm-audit"]
```

## Invocation and Usage

Unless opted out, pdm-audit will run as a post-install hook. This means, that every time a package is added, removed, updated or installed, the auditing will take place.

It will export the currentbstate of the lock file to requirements.txt and run the auditor against it.

It is also possible to run an explicit audit by invoking the `pdm audit` command.

### Command-line options

Invoking the plug-in from cli is pretty easy. It provides an `audit` command to pdm.

#### Verbosity

By default, it uses the info verbosity of the logger. The [pdm-pfsc](https://pypi.org/projects/pdm-pfsc) logger also provides log-levels for Debug and Trace.

Adding the `-v` to the `audit` command increases the verbosity to DEBUG.

Adding the `-vv` to the `audit` command increases the verbosity to TRACE and also important function calls. 

#### PIP-Audit options

You can pass an arbitrary `pip-audit` argument to `pdm audit`. Especially the following might be useful:

 - `-S`, `--strict` 
 - `-l`, `--local`
 - `-s`, `--vulnerability-servers` (one of `osv` or `pypi`)
 - `-f`, `--format` (one of `columns`, `json`, `cyclonedx-json`, `cyclonedx-xml` or `markdown`)
 - `-o`, `--output` `FILE`
 - `-d`, `--dry-run`
 - `-t`, `--timeout` `SECONDS`

The hook cannot be configured this way as it always produces a temporary JSON file, which will be parsed afterwards.

### Configuration options

| Value (in `pdm.toml`)               | Description                        | Default Value | Environment-Variable          |
| ----------------------------------- | ---------------------------------- | ------------- | ----------------------------- |
| plugin.audit.post_installation_hook | Enable / Disable Post-Install-Hook | True          | PDM_AUDIT_PLUGIN_HOOK_PI      |
| plugin.audit.hook_verbose           | Equal to calling `pdm audit -vv`   | False         | PDM_AUDIT_PLUGIN_HOOK_VERBOSE |
| plugin.audit.repeatable_audit       | Add hashes to requirements.txt     | True          |            ---                |

So, if you temporarily want to disable the audit during installation, you can run 

```shell
$ PDM_AUDIT_PLUGIN_HOOK_PI=False pdm install 
```

Repeatable audits are enabled by default. This will export the hashes of all requirements to the `requirements.txt` which is used for `pip-audit`. This unfortunately will fail, if your project depends on editable installs, as there are no hashes available. Hence auditing will fail. So, run `pdm config --local plugin.audit.repeatable_audit False` to disable exporting the hashes. This will add a string value. It will automatically be converted to a boolean value. It must be equal to 'true' or '1' - blanks will be removed and casing will be enabled.

## Contributions

### Issues

Issues are always welcome, even though I do not intend to include any bugs in my code by purpose.

Please note, that this project is developed in my free-time. Issues may take their times and I sometimes need some more information to reproduce certain environments or circumstances. It may also require you to test some alpha versions. So please be patient and willing to help me solve your issues.

If possible, add stack-traces with `-vv` appended to `pdm audit` or in case of using the hook, make sure, that `PDM_AUDIT_PLUGIN_HOOK_VERBOSE` is set to `True`.

### Bugfixes and Features

At the moment, I don't have a stable testing and formatting strategy yet. I am willing to accept contributions, but may be picky with some details.

## Roadmap to v1.0

The following issues are open:

 - [ ] `fix` mode -> Update dependency to a version with solved issues using `pdm update`
 - [ ] Better integration of `pip-audit` and its CLI arguments
 - [ ] Unit tests
 - [ ] Coding guidelines and style checking
