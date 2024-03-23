
from pdm.project import Project

from .plugin import Auditor


def run_pdm_audit_signal(project: Project, candidates: dict, dry_run: bool, **kwargs) -> None:
    del candidates, kwargs
    run: bool = project.config["tools.pdm.audit_plugin.post_install_hook"] or False
    if not dry_run and run:
        auditor: Auditor = Auditor()
        auditor.audit(project)
