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
    project: Project, candidates: dict, dry_run: bool, **kwargs
) -> None:
    del candidates, kwargs
    run: bool = (
        project.config["tools.pdm.audit_plugin.post_install_hook"] or False
    )
    if not dry_run and run:
        auditor: Auditor = Auditor()
        auditor.audit(
            project,
            project.config["tools.pdm.audit_plugin.hook_verbose"] or False,
        )
