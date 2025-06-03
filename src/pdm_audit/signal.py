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

from pdm_pfsc.logging import (
    setup_logger,
    update_logger_from_project_ui,
)

from .config import Config  
from .plugin import Auditor


def run_pdm_audit_signal(
    project: Project, packages: list, dry_run: bool = False, **kwargs
) -> None:
    del packages, kwargs
    config = Config(project)
    run: bool = config.use_hook
    setup_logger(config.hook_verbose)
    update_logger_from_project_ui(project.core.ui)
    if not dry_run and run:
        auditor: Auditor = Auditor()
        auditor.audit(
            project,
            config.hook_verbose,
        )
