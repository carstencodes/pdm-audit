from abc import abstractmethod, ABC
from pathlib import Path
from typing import Optional

from pdm_pfsc.proc import CliRunnerMixin


class Executor(ABC):
    @abstractmethod
    def execute(self) -> int:
        raise NotImplementedError()


class PdmExportDependenciesExecutor(Executor, CliRunnerMixin):
    def __init__(self, out_file: Path) -> None:
        self.__out_file = out_file

    @property
    def out_file(self) -> Path:
        return self.__out_file

    def execute(self) -> int:
        pdm: Optional[Path] = self._which("pdm")
        if pdm is None:
            return -1

        exit_code, _, _ = self.run(pdm, ("export", "-f", "requirements", "-G", ":all", "-o", str(self.out_file)))

        return exit_code


class PipAuditExecutor(Executor, CliRunnerMixin):
    def __init__(self, input_file: Path, *args: str) -> None:
        self.__input_file = input_file
        self.__args = args

    @property
    def input_file(self) -> Path:
        return self.__input_file

    @property
    def args(self) -> tuple[str, ...]:
        return self.__args

    def execute(self) -> int:
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

        exit_code, _, _ = self.run(pip_audit, arg_items)

        return exit_code
