from abc import abstractmethod, ABC
from pathlib import Path
from typing import Optional

from pdm_pfsc.logging import traced_function, logger
from pdm_pfsc.proc import CliRunnerMixin


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
    def __init__(self, out_file: Path) -> None:
        self.__out_file = out_file

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

        exit_code, _, _ = self.run(pdm, (
            "export",
            "-f",
            "requirements",
            "-G",
            ":all",
            "-o",
            str(self.out_file)),
        )

        return exit_code


class PipAuditExecutor(Executor, CliRunnerMixin):
    """"""
    def __init__(self, input_file: Path, *args: str) -> None:
        """"""
        self.__input_file = input_file
        self.__args = args

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
        pip_audit: Path = self._which("pip-audit")
        if pip_audit is None:
            return -1

        arguments = [a for a in self.args]
        arguments.append("--require-hashes")
        arguments.append("--disable-pip")
        arguments.append("--skip-editable")
        arguments.append("--progress-spinner")
        arguments.append("off")
        arguments.append("--requirement")
        arguments.append(str(self.input_file))

        arg_items = tuple(arguments)

        exit_code, stdout, stderr = self.run(pip_audit, arg_items)

        if exit_code == 0:
            if len(stdout) > 0:
                logger.info(stdout)
            else:
                logger.info("0 vulnerabilities found.")
        else:
            logger.warning(stderr)

        return exit_code
