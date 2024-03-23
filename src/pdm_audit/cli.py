from pdm.core import Core
from pdm.project import ConfigItem

from pdm_audit.plugin import AuditCommand
from pdm.signals import post_install

from pdm_audit.signal import run_pdm_audit_signal


def main(core: Core) -> None:
    """

    Parameters
    ----------
    core: _CoreLike :


    Returns
    -------

    """
    core.register_command(AuditCommand)
    core.add_config("tools.pdm.audit_plugin.post_install_hook", ConfigItem(
        "If set to true, run pdm audit after installation", True, env_var="PDM_AUDIT_PLUGIN_HOOK_PI"))

    post_install.connect(run_pdm_audit_signal)
