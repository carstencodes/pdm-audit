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
from pdm.core import Core
from pdm.project import ConfigItem
from pdm.signals import post_install

from pdm_audit.plugin import AuditCommand
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
    core.add_config(
        "plugin.audit.post_install_hook",
        ConfigItem(
            "If set to true, run pdm audit after installation",
            True,
            env_var="PDM_AUDIT_PLUGIN_HOOK_PI",
        ),
    )
    core.add_config(
        "plugin.audit.hook_verbose",
        ConfigItem(
            "If set to true, run the hook in verbose mode",
            True,
            env_var="PDM_AUDIT_PLUGIN_HOOK_VERBOSE",
        ),
    )

    post_install.connect(run_pdm_audit_signal)
