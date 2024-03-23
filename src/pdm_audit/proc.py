from os import environ, pathsep
from pathlib import Path
from subprocess import run as stdlib_run_process
from sys import platform
from typing import Protocol, Union, Optional, cast


class _CompletedProcessLike(Protocol):
    """"""

    @property
    def returncode(self) -> int:
        """"""
        raise NotImplementedError()

    @property
    def stdout(self) -> str:
        """"""
        raise NotImplementedError()

    @property
    def stderr(self) -> str:
        """"""
        raise NotImplementedError()


class _ProcessRunningCallable(Protocol):
    """"""

    def __call__(
        self,
        cmd: list[str],
        *,
        check: bool,
        capture_output: bool,
        cwd: Optional[Union[str, Path]],
        encoding: str = "utf-8",
    ) -> _CompletedProcessLike:
        raise NotImplementedError()


class ProcessRunner:
    """"""

    run_process: Optional[_ProcessRunningCallable] = None
    def _run_process(
        self,
        cmd: list[str],
        *,
        check: bool,
        capture_output: bool,
        cwd: Optional[Union[str, Path]],
        encoding: str = "utf-8",
    ) -> _CompletedProcessLike:
        """

        Parameters
        ----------
        cmd: list[str] :

        * :

        check: bool :

        capture_output: bool :

        cwd: Optional[Union[str, Path]] :

        encoding: str :
             (Default value = "utf-8")

        Returns
        -------

        """
        if self.run_process is not None:
            run_proc: _ProcessRunningCallable = cast(
                _ProcessRunningCallable, self.run_process
            )
            return run_proc(
                cmd,
                check=check,
                capture_output=capture_output,
                cwd=cwd,
                encoding=encoding,
            )

        return stdlib_run_process(
            cmd,
            check=check,
            capture_output=capture_output,
            cwd=cwd,
            encoding=encoding,
        )


class CliRunnerMixin(ProcessRunner):
    """"""

    def _which(
        self, exec_name: str, extension: Optional[str] = None
    ) -> Optional[Path]:
        """

        Parameters
        ----------
        exec_name: str :

        extension: Optional[str] :
             (Default value = None)

        Returns
        -------

        """
        search_path = environ["PATH"]
        if search_path is None or len(search_path) == 0:
            return None

        extension = ".exe" if extension is None and platform == "win32" else ""
        executable_full_name = exec_name + extension
        paths = search_path.split(pathsep)
        for path in [Path(p) for p in paths]:
            file_path = path / executable_full_name
            if file_path.is_file():
                return file_path

        return None

    def run(
        self,
        /,
        executable: Path,
        args: tuple[str, ...],
        *,
        raise_on_exit: bool = False,
        cwd: Optional[Path] = None,
    ) -> tuple[int, str, str]:
        """

        Parameters
        ----------
        / :

        executable: Path :

        args: tuple[str, ...] :

        * :

        raise_on_exit: bool :
             (Default value = False)
        cwd: Optional[Path] :
             (Default value = None)

        Returns
        -------

        """
        cmd = [str(executable)]
        for arg in args:
            cmd.append(arg)

        completed: _CompletedProcessLike = self._run_process(
            cmd,
            check=False,
            capture_output=True,
            cwd=cwd,
            encoding="utf-8",
        )

        if raise_on_exit and completed.returncode != 0:
            raise SystemError(
                completed.returncode, completed.stdout, completed.stderr
            )

        return (
            completed.returncode,
            completed.stdout,
            completed.stderr,
        )