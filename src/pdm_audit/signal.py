#
# SPDX-License-Identifier: MIT
#
# Copyright (c) 2021-2025 Carsten Igel.
#
# This file is part of pdm-audit
# (see https://github.com/carstencodes/pdm-audit).
#
# This file is published using the MIT license.
# Refer to LICENSE for more information
#

from pdm.project import Project

from .plugin import Auditor


def run_pdm_audit_signal(
    project: Project, packages: list, dry_run: bool = False, **kwargs
) -> None:
    del packages, kwargs
    run: bool = project.config["plugin.audit.post_install_hook"] or False
    if not dry_run and run:
        auditor: Auditor = Auditor()
        auditor.audit(
            project,
            project.config["plugin.audit.hook_verbose"] or False,
        )
