import contextlib
import os
import tempfile
from argparse import ArgumentParser, Namespace
from collections.abc import Iterator
from pathlib import Path
from typing import Final

from pdm.cli.commands.base import BaseCommand
from pdm import core
from pdm.project import Project
from pdm_pfsc.logging import traced_function, logger, \
    update_logger_from_project_ui, setup_logger

from .executor import PipAuditExecutor, PdmExportDependenciesExecutor, \
    Executor, ExecutionError


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
        parser.add_argument("auditor_arguments",
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
                            action="store")

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
        auditor.audit(project, *args)


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
    def audit(self, project: Project, *args: str) -> None:
        with _cwd(project.root):
            logger.info("Auditing packages installed by PDM ...")
            with tempfile.NamedTemporaryFile(
                suffix="req.txt",
                prefix="pdm_audit",
            ) as req_file:
                logger.debug("Exporting requirements.txt file from PDM")
                req_file_path: Path = Path(req_file.name).resolve()
                export: Executor = PdmExportDependenciesExecutor(req_file_path)
                audit: Executor = PipAuditExecutor(req_file_path, *args)

                try:
                    Executor.execute_chain(
                        export,
                        audit
                    )
                except ExecutionError as e:
                    logger.exception(
                        "Auditing failed.",
                        exc_info=e,
                        stack_info=False,
                    )
