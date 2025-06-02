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

from pdm.project.core import Project
from typing import Optional

class Config:
    def __init__(self, project: "Project") -> None:
        self.__project = project

    @property
    def use_hook(self) -> "bool":
        return Config._str_to_bool(self.__project.config["plugin.audit.post_installation_hook"], True)

    @property
    def hook_verbose(self) -> "bool":
        return Config._str_to_bool(self.__project.config["plugin.audit.hook_verbose"], False)

    @property
    def repeatable(self) -> "bool":
        return Config._str_to_bool(self.__project.config["plugin.audit.repeatable_audit"], True)

    @staticmethod
    def _str_to_bool(value: "Optional[str]", default_value: "bool") -> "bool":
        if value is None:
            return default_value

        parseable = value.strip().lower()
        return parseable in ("true", "1")
