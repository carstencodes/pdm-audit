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
from pdm.signals import post_install

from pdm_audit.plugin import AuditCommand
from pdm_audit.signal import run_pdm_audit_signal

from .config import config_definition


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
        config_definition.config_names.use_hook,
        config_definition.config_items.use_hook,
    )
    core.add_config(
        config_definition.config_names.hook_verbose,
        config_definition.config_items.hook_verbose,
    )
    core.add_config(
        config_definition.config_names.repeatable,
        config_definition.config_items.repeatable,
    )

    post_install.connect(run_pdm_audit_signal)
