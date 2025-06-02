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
import contextlib
import os
import tempfile
from argparse import ArgumentParser, Namespace
from collections.abc import Iterator
from pathlib import Path
from typing import Final

from pdm.cli.commands.base import BaseCommand
from pdm.project import Project
from pdm_pfsc.logging import (
    logger,
    setup_logger,
    traced_function,
    update_logger_from_project_ui,
)

from .config import Config
from .executor import (
    ExecutionError,
    Executor,
    PdmExportDependenciesExecutor,
    PipAuditExecutor,
)


class AuditCommand(BaseCommand):
    # Justification: Fulfill a protocol
    name: Final[str] = "audit"  # pylint: disable=C0103
    description: str = "Runs an audit tool on the packages installed by PDM"

    def add_arguments(self, parser: ArgumentParser) -> None:
        """

        Parameters
        ----------
        parser: ArgumentParser :


        Returns
        -------

        """
        parser.add_argument(
            "auditor_arguments",
            nargs="*",
            default=[],
            help="Arguments passed to pip-audit - should be preceded by --\n"
            "The arguments to apply to maybe\n"
            "     -S/--strict\n"
            "     -l/--local\n"
            "     -s/--vulnerability-servers osv|pypi\n"
            "     -f/--format columns|json|cyclonedx-json|cyclonedx-xml|markdown\n"
            "     -o/--output FILE\n"
            "     -d/--dry-run\n"
            "     --timeout TIMEOUT (in seconds)",
            action="store",
        )

    def handle(self, project: Project, options: Namespace) -> None:
        """

        Parameters
        ----------
        project: _ProjectLike :

        options: Namespace :


        Returns
        -------

        """
        # This will not handling tracing or related parts
        # Should be evaluated at start-up time
        if hasattr(options, "verbose"):
            setup_logger(options.verbose)
        update_logger_from_project_ui(project.core.ui)

        args = tuple(options.auditor_arguments or [])
        auditor: Auditor = Auditor()
        auditor.audit(project, options.verbose or False, *args)


@contextlib.contextmanager
def _cwd(path: Path) -> Iterator[None]:
    old_cwd = os.getcwd()
    try:
        os.chdir(path)
        yield None
    finally:
        os.chdir(old_cwd)


class Auditor:
    @traced_function
    def audit(self, project: Project, verbose: bool, *args: str) -> None:
        with _cwd(project.root):
            logger.info("Auditing packages installed by PDM ...")
            repeatable = Config(project).repeatable
            
            with tempfile.NamedTemporaryFile(
                suffix="req.txt",
                prefix="pdm_audit",
            ) as req_file:
                logger.debug("Exporting requirements.txt file from PDM")
                req_file_path: Path = Path(req_file.name).resolve()
                export: Executor = PdmExportDependenciesExecutor(
                    req_file_path, repeatable
                )
                audit: Executor = PipAuditExecutor(
                    req_file_path, project, verbose, repeatable, *args
                )

                try:
                    Executor.execute_chain(export, audit)
                except ExecutionError as e:
                    logger.exception(
                        "Auditing failed.",
                        exc_info=e,
                        stack_info=False,
                    )
