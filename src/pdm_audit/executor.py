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
from abc import ABC, abstractmethod
from pathlib import Path
from os import getenv as os_environ, environ as os_environment, pathsep as os_pathsep
from shutil import which
from sys import version_info as sys_version_info, executable as sys_executable
from typing import Optional

from pdm.project import Project
from pdm_pfsc.logging import logger, traced_function
from pdm_pfsc.proc import CliRunnerMixin, ProcessRunner

from .updates import get_dependencies


class ExecutionError(Exception):
    def __init__(self, executor: "Executor") -> None:
        message = f"Failed to execute {executor.name}: {executor.description}"
        super().__init__(message)


class Executor(ABC):
    """"""

    @property
    @abstractmethod
    def name(self) -> str:
        """"""
        raise NotImplementedError()

    @property
    @abstractmethod
    def description(self) -> str:
        """"""
        raise NotImplementedError()

    @abstractmethod
    def execute(self) -> int:
        """"""
        raise NotImplementedError()

    @staticmethod
    def execute_chain(*executors: "Executor") -> None:
        """"""
        for executor in executors:
            if executor.execute() != 0:
                raise ExecutionError(executor)


class PdmExportDependenciesExecutor(Executor, CliRunnerMixin):
    def __init__(self, out_file: Path, write_hashes: bool = False) -> None:
        self.__out_file = out_file
        self.__write_hashes = write_hashes

    @property
    def name(self) -> str:
        """"""
        return "Export"

    @property
    def description(self) -> str:
        """"""
        return f"Export dependencies to {self.out_file}"

    @property
    def out_file(self) -> Path:
        """"""
        return self.__out_file

    @traced_function
    def execute(self) -> int:
        """"""
        pdm: Optional[Path] = self._which("pdm")
        if pdm is None:
            return -1

        args = [
            "-f",
            "requirements",
            "-G",
            ":all",
            "-o",
            str(self.out_file),
        ]

        if not self.__write_hashes:
            args.append("--no-hashes")

        call = ["export"]
        call.extend(args)

        exit_code, _, err = self.run(
            pdm,
            tuple(call),
        )

        if exit_code > 0:
            logger.error("Error while exporting lock file.")
            logger.warning(err)

        return exit_code


class PipAuditLocator(ProcessRunner):
    def __init__(self, python_interpreter: "Path", python_path: "Optional[Path]", *cmd_args: "str") -> None:
        self.__interpreter = python_interpreter
        self.__python_path = python_path
        self.__args: "tuple[str, ...]" = cmd_args

    @property
    def interpreter(self) -> "Path":
        return self.__interpreter
    
    @property
    def args(self) -> "list[str]":
        return list(self.__args)

    @property
    def proc_env(self):
        PYTHONPATH = "PYTHONPATH"
        env = dict()
        env.update(os_environment)
        if self.__python_path is not None:
            env[PYTHONPATH] = os_pathsep.join([str(self.__python_path), os_environ(PYTHONPATH, "")])

        return env
    
    @traced_function
    def supports_pip_audit(self) -> bool:
        script = "import pip_audit; import pip;"

        args = list(self.__args) + ["-c", script]
        logger.debug("Running '%s' with args %s and python_path '%s'", self.__interpreter, args, self.__python_path)

        cmd = [str(self.__interpreter)] + args
        result = self._run_process(cmd, check=False, capture_output=True, cwd=".", env=self.proc_env)

        logger.debug("Process result:\n\texit_code: %i\n\tstd_out: %s\n\tstd_err: %s",
                     result.returncode,
                     result.stdout,
                     result.stderr,
                     )
        return result.returncode == 0

    @classmethod
    def from_pdm_env(cls) -> "PipAuditLocator":
        pdm = which("pdm")
        if pdm is None:
            raise FileNotFoundError("pdm")
        pdm_exe = Path(pdm)
        return PipAuditLocator(pdm_exe, None, "run", "python")
    
    @classmethod
    def from_current_env(cls, project: "Project") -> "PipAuditLocator":
        python_interpreter = sys_version_info
        plugins_folder = project.root / ".pdm-plugins" / "lib" / f"python{python_interpreter.major}.{python_interpreter.minor}" / "site-packages"
        if project.is_global or not plugins_folder.exists():
            plugins_folder = None
        return PipAuditLocator(Path(sys_executable), plugins_folder)
    
    @classmethod
    def from_project(cls, project: "Project") -> "Optional[PipAuditLocator]":
        return PipAuditLocator(project.python.executable, None)

    @classmethod
    def from_project_env(cls, project: "Project") -> "Optional[PipAuditLocator]":
        return PipAuditLocator(project.environment.interpreter.executable, None)


class _PipAuditNotFoundError(Exception):
    pass


class PipAuditExecutor(Executor, CliRunnerMixin):
    """"""

    def __init__(
        self,
        input_file: Path,
        project: Project, 
        verbose: bool = False,
        repeatable: bool = False,
        *args: str,
    ) -> None:
        """"""
        self.__input_file = input_file
        self.__args = args
        self.__verbose = verbose
        self.__repeatable = repeatable
        self.__project = project

    @property
    def name(self) -> str:
        """"""
        return "Auditor"

    @property
    def description(self) -> str:
        """"""
        return f"Running pip-audit on exported file: {self.__input_file}"

    @property
    def input_file(self) -> Path:
        """"""
        return self.__input_file

    @property
    def args(self) -> tuple[str, ...]:
        """"""
        return self.__args

    @traced_function
    def execute(self) -> int:
        """"""
        # Run pip_audit as python main module
        prepend_args: list[str] = ["-m", "pip_audit"]
        
        arguments = prepend_args + [a for a in self.args]
        if self.__repeatable:
            arguments.append("--require-hashes")
            arguments.append("--disable-pip")
        arguments.append("--skip-editable")
        arguments.append("--progress-spinner")
        arguments.append("off")
        arguments.append("--format")
        arguments.append("json")
        arguments.append("--requirement")
        arguments.append(str(self.input_file))

        try:
            location = self.__find_interpreters_supporting_pip_audit()
            interpreter = location.interpreter
            env = location.proc_env
            arguments = location.args + arguments
        except _PipAuditNotFoundError:
            logger.error("Failed to find a python environment that supports `pip_audit` module")
            return 125
        
        arg_items = tuple(arguments)

        exit_code, stdout, stderr = self.run(interpreter, arg_items, env=env)

        exit_code_no_vulnerabilities = 0
        exit_code_has_vulnerabilities = 1

        if exit_code in (
            exit_code_no_vulnerabilities,
            exit_code_has_vulnerabilities,
        ):
            if len(stdout) > 0:
                d = get_dependencies(stdout)
                if d is not None:
                    num_vulnerabilities = self._get_number_of_vulnerabilities(
                        d, self.__verbose
                    )
                    if num_vulnerabilities > 0:
                        logger.warning(
                            "%i vulnerabilities found", num_vulnerabilities
                        )
                    else:
                        logger.info(
                            "%i vulnerabilities found", num_vulnerabilities
                        )
                else:
                    logger.warning(
                        "Failed to get dependencies with vulnerabilities"
                    )
            elif exit_code == exit_code_has_vulnerabilities:
                logger.warning(
                    "Vulnerable packages found. Failed to get details"
                )
            else:
                logger.info("0 vulnerabilities found.")

            return 0
        else:
            logger.warning(stderr)

        return exit_code
    
    @traced_function
    def __find_interpreters_supporting_pip_audit(self) -> "PipAuditLocator":
        for locator in [
            PipAuditLocator.from_pdm_env(),
            PipAuditLocator.from_current_env(self.__project),
            PipAuditLocator.from_project(self.__project),
            PipAuditLocator.from_project_env(self.__project),
        ]:
            if locator is None:
                continue
            if locator.supports_pip_audit():
                logger.debug("'%s' supports pip_audit. Using this interpreter.", locator.interpreter)
                return locator
            logger.debug("'%s' does not support pip_audit. Searching next ...", locator.interpreter)
            
        logger.debug("No interpreter found.")
        raise _PipAuditNotFoundError()

    @traced_function
    def _get_number_of_vulnerabilities(
        self, dependencies, log_vulnerabilities=False
    ):
        def get_vulnerability_id(vuln) -> str:
            if len(vuln.aliases) > 0:
                return f"{vuln.id},{','.join(vuln.aliases)}"
            return vuln.id

        def get_solved_versions(vuln) -> "str | None":
            if len(vuln.fixed_versions) > 0:
                return ",".join(vuln.fixed_versions)
            return None

        num_vulnerabilities = 0
        for v in [d for d in dependencies.dependencies if len(d.vulns) > 0]:
            for vulnerability in v.vulns:
                num_vulnerabilities = num_vulnerabilities + 1
                fixed_versions = get_solved_versions(vulnerability)
                if log_vulnerabilities:

                    logger.info(
                        (
                            "Package %s (Version %s) is vulnerable by %s."
                            "Please upgrade to %s. Details: %s"
                        ),
                        v.name,
                        v.version,
                        get_vulnerability_id(vulnerability),
                        fixed_versions or "UNSOLVED",
                        vulnerability.description,
                    )
                if fixed_versions is not None:
                    logger.warning(
                        "Update %s to version %s", v.name, fixed_versions
                    )
                else:
                    logger.warning(
                        "Packages %s has an unresolved vulnerability", v.name
                    )
        return num_vulnerabilities
