import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandResult:
    command: list[str]
    return_code: int
    stdout: str
    stderr: str


class CommandRunner:
    def run(self, command: list[str], *, cwd: str | None = None, timeout_seconds: int = 300) -> CommandResult:
        completed = subprocess.run(
            command,
            cwd=cwd,
            timeout=timeout_seconds,
            check=False,
            capture_output=True,
            text=True,
        )
        return CommandResult(
            command=command,
            return_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
