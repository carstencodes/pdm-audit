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
from pdm.project import ConfigItem

from functools import cached_property
from typing import Optional


class _ConfigNames:
    @property
    def use_hook(self) -> "str":
        return "plugin.audit.post_install_hook"

    @property
    def hook_verbose(self) -> "str":
        return "plugin.audit.hook_verbose"
    
    @property
    def repeatable(self) -> "str":
        return "plugin.audit.repeatable_audit"

class _ConfigItems:
    @cached_property
    def use_hook(self) -> "ConfigItem":
        return ConfigItem(
            "If set to true, run pdm audit after installation",
            True,
            env_var="PDM_AUDIT_PLUGIN_HOOK_PI",
        )

    @cached_property
    def hook_verbose(self) -> "ConfigItem":
        return ConfigItem(
            "If set to true, run the hook in verbose mode",
            False,
            env_var="PDM_AUDIT_PLUGIN_HOOK_VERBOSE",
        )
    
    @cached_property
    def repeatable(self) -> "ConfigItem":
        return ConfigItem(
            "If set to true, run pdm audit with repeatable audits. "
            "This will include hashes and hence cannot be used for "
            "references with local references",
            True,
        )

class _ConfigDefinition:
    def __init__(self) -> "None":
        self.__config_items = _ConfigItems()
        self.__config_names = _ConfigNames()

    @property
    def config_items(self) -> "_ConfigItems":
        return self.__config_items

    @property
    def config_names(self) -> "_ConfigNames":
        return self.__config_names


config_definition = _ConfigDefinition()


class Config:
    def __init__(self, project: "Project") -> None:
        self.__project = project
        self.__definition = config_definition

    @property
    def use_hook(self) -> "bool":
        return Config._str_to_bool(self.__project.config[self.config_names.use_hook], self.config_items.use_hook.default)

    @property
    def hook_verbose(self) -> "bool":
        return Config._str_to_bool(self.__project.config[self.config_names.hook_verbose], self.config_items.hook_verbose.default)

    @property
    def repeatable(self) -> "bool":
        return Config._str_to_bool(self.__project.config[self.config_names.repeatable], self.config_items.repeatable.default)

    @property
    def config_items(self) -> "_ConfigItems":
        return self.__definition.config_items

    @property
    def config_names(self) -> "_ConfigNames":
        return self.__definition.config_names
    
    @staticmethod
    def _str_to_bool(value: "Optional[str]", default_value: "bool") -> "bool":
        if value is None:
            return default_value

        parseable = value.strip().lower()
        return parseable in ("true", "1")
