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
from dataclasses import dataclass, field
from json import loads


@dataclass
class DependenciesInfo:
    """"""

    dependencies: "list[DependencyInfo]" = field(default_factory=list)


@dataclass
class DependencyInfo:
    """"""

    name: str = field()
    version: str = field()
    vulns: "list[VulnerabilityInfo]" = field(default_factory=list)


@dataclass
class VulnerabilityInfo:
    """"""

    id: str = field()
    description: str = field()
    fixed_versions: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)


def get_dependencies(json_str: str) -> "DependenciesInfo | None":
    """"""
    data_dict: dict
    try:
        data_dict = loads(json_str)
    except:
        return None
    if "dependencies" in data_dict:
        items = data_dict["dependencies"]
        instances: list[DependencyInfo] = []
        for item in [i for i in items if isinstance(i, dict)]:
            name = item.get("name", None)
            version = item.get("version", None)
            vulns = item.get("vulns", [])
            vulnerabilities: list[VulnerabilityInfo] = []
            if isinstance(vulns, list):
                for vuln in vulns:
                    v_id = vuln.get("id", None)
                    fixed_versions = vuln.get("fix_versions", [])
                    aliases = vuln.get("aliases", [])
                    description = vuln.get("description", None)
                    vulnerabilities.append(
                        VulnerabilityInfo(
                            id=v_id or "UNKNOWN",
                            description=description or "UNKNOWN",
                            aliases=aliases or [],
                            fixed_versions=fixed_versions or [],
                        )
                    )
            instance = DependencyInfo(
                name=name or "UNKNOWN",
                version=version or "UNKNOWN",
                vulns=vulnerabilities,
            )
            instances.append(instance)
        return DependenciesInfo(dependencies=instances)
    return DependenciesInfo(dependencies=[])
