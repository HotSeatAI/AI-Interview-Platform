import os
import subprocess
import tempfile
import time
from pathlib import Path

from app.schemas.code import (
    CodeRunRequest,
    CodeRunResponse,
)

# Env vars user-submitted code is allowed to see when it runs. This is
# an allowlist, not a blocklist: subprocess.run() defaults to inheriting
# the FULL parent environment (GEMINI_API_KEYS, SECRET_KEY, DATABASE_URL,
# GOOGLE_CLIENT_SECRET, ...) when no `env=` is given, and stdout/stderr
# from these subprocesses is sent straight back to the browser's console
# output panel. Submitted code that does `print(os.environ)` (or the
# equivalent in any supported language) would otherwise leak every
# backend secret directly onto the screen. Only what each toolchain
# needs to actually run is included here.
_SANDBOX_ENV_ALLOWLIST = (
    "PATH",
    "HOME",
    "LANG",
    "LC_ALL",
    "TMPDIR",
    "JAVA_HOME",
)


def _sandbox_env() -> dict:
    return {
        key: os.environ[key]
        for key in _SANDBOX_ENV_ALLOWLIST
        if key in os.environ
    }


class CodeExecutionService:
    TIMEOUT_SECONDS = 2

    def run_code(
        self,
        request: CodeRunRequest,
    ) -> CodeRunResponse:
        if request.language == "python":
            return self._run_python(request)

        if request.language == "cpp":
            return self._run_cpp(request)

        if request.language == "java":
            return self._run_java(request)

        if request.language == "javascript":
            return self._run_javascript(request)

        if request.language == "c":
            return self._run_c(request)

        if request.language == "verilog":
            return self._run_verilog(request)

        if request.language == "sql":
            return self._run_sql(request)

        return self._not_implemented(request.language)

    def _run_python(
        self,
        request: CodeRunRequest,
    ) -> CodeRunResponse:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "main.py"

            file_path.write_text(
                request.code,
                encoding="utf-8",
            )

            start = time.perf_counter()

            try:
                result = subprocess.run(
                    ["python3", str(file_path)],
                    input=request.stdin,
                    text=True,
                    capture_output=True,
                    timeout=self.TIMEOUT_SECONDS,
                    env=_sandbox_env(),
                )

                execution_time = (time.perf_counter() - start) * 1000

                if result.returncode != 0:

                    return CodeRunResponse(
                        status="runtime_error",
                        stdout=result.stdout,
                        stderr=result.stderr,
                        execution_time_ms=round(
                            execution_time,
                            2,
                       ),
                        memory_kb=None,
                    )

                return CodeRunResponse(
                    status="accepted",
                    stdout=result.stdout,
                    stderr="",
                    execution_time_ms=round(
                        execution_time,
                        2,
                    ),
                    memory_kb=None,
                )

            except subprocess.TimeoutExpired:
                return CodeRunResponse(
                    status="time_limit_exceeded",
                    stdout="",
                    stderr="Time Limit Exceeded",
                    execution_time_ms=None,
                    memory_kb=None,
                )

            except Exception as exception:
                return CodeRunResponse(
                    status="internal_error",
                    stdout="",
                    stderr=str(exception),
                    execution_time_ms=None,
                    memory_kb=None,
                )

    def _run_cpp(
        self,
        request: CodeRunRequest,
    ) -> CodeRunResponse:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source_file = temp_path / "main.cpp"
            executable = temp_path / "main"

            source_file.write_text(
                request.code,
                encoding="utf-8",
            )

            compile_start = time.perf_counter()

            compile_process = subprocess.run(
                [
                    "g++",
                    str(source_file),
                    "-std=c++17",
                    "-O2",
                    "-o",
                    str(executable),
                ],
                capture_output=True,
                text=True,
                cwd=temp_path,
                env=_sandbox_env(),
            )

            if compile_process.returncode != 0:
                compile_time = (time.perf_counter() - compile_start) * 1000

                return CodeRunResponse(
                    status="compilation_error",
                    stdout="",
                    stderr=compile_process.stderr,
                    execution_time_ms=round(
                        compile_time,
                        2,
                    ),
                    memory_kb=None,
                )

            execution_start = time.perf_counter()

            try:
                execution = subprocess.run(
                    [str(executable)],
                    input=request.stdin,
                    capture_output=True,
                    text=True,
                    timeout=self.TIMEOUT_SECONDS,
                    cwd=temp_path,
                    env=_sandbox_env(),
                )

                execution_time = (time.perf_counter() - execution_start) * 1000

                if execution.returncode != 0:
                    return CodeRunResponse(
                        status="runtime_error",
                        stdout=execution.stdout,
                        stderr=execution.stderr,
                        execution_time_ms=round(
                            execution_time,
                            2,
                        ),
                        memory_kb=None,
                    )

                return CodeRunResponse(
                    status="accepted",
                    stdout=execution.stdout,
                    stderr="",
                    execution_time_ms=round(
                        execution_time,
                        2,
                    ),
                    memory_kb=None,
                )

            except subprocess.TimeoutExpired:
                return CodeRunResponse(
                    status="time_limit_exceeded",
                    stdout="",
                    stderr="Time Limit Exceeded",
                    execution_time_ms=None,
                    memory_kb=None,
                )

            except Exception as exception:
                return CodeRunResponse(
                    status="internal_error",
                    stdout="",
                    stderr=str(exception),
                    execution_time_ms=None,
                    memory_kb=None,
                )

    def _run_java(
        self,
        request: CodeRunRequest,
    ) -> CodeRunResponse:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source_file = temp_path / "Main.java"

            source_file.write_text(
                request.code,
                encoding="utf-8",
            )

            compile_start = time.perf_counter()

            compile_process = subprocess.run(
                [
                    "javac",
                    str(source_file),
                ],
                capture_output=True,
                text=True,
                cwd=temp_path,
                env=_sandbox_env(),
            )

            if compile_process.returncode != 0:
                compile_time = (time.perf_counter() - compile_start) * 1000

                return CodeRunResponse(
                    status="compilation_error",
                    stdout="",
                    stderr=compile_process.stderr,
                    execution_time_ms=round(
                        compile_time,
                        2,
                    ),
                    memory_kb=None,
                )

            execution_start = time.perf_counter()

            try:
                execution = subprocess.run(
                    [
                        "java",
                        "-cp",
                        str(temp_path),
                        "Main",
                    ],
                    input=request.stdin,
                    capture_output=True,
                    text=True,
                    timeout=self.TIMEOUT_SECONDS,
                    cwd=temp_path,
                    env=_sandbox_env(),
                )

                execution_time = (time.perf_counter() - execution_start) * 1000

                if execution.returncode != 0:
                    return CodeRunResponse(
                        status="runtime_error",
                        stdout=execution.stdout,
                        stderr=execution.stderr,
                        execution_time_ms=round(
                            execution_time,
                            2,
                        ),
                        memory_kb=None,
                    )

                return CodeRunResponse(
                    status="accepted",
                    stdout=execution.stdout,
                    stderr="",
                    execution_time_ms=round(
                        execution_time,
                        2,
                    ),
                    memory_kb=None,
                )

            except subprocess.TimeoutExpired:
                return CodeRunResponse(
                    status="time_limit_exceeded",
                    stdout="",
                    stderr="Time Limit Exceeded",
                    execution_time_ms=None,
                    memory_kb=None,
                )

            except Exception as exception:
                return CodeRunResponse(
                    status="internal_error",
                    stdout="",
                    stderr=str(exception),
                    execution_time_ms=None,
                    memory_kb=None,
                )

    def _run_javascript(
        self,
        request: CodeRunRequest,
    ) -> CodeRunResponse:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source_file = temp_path / "main.js"

            source_file.write_text(
                request.code,
                encoding="utf-8",
            )

            execution_start = time.perf_counter()

            try:
                execution = subprocess.run(
                    [
                        "node",
                        str(source_file),
                    ],
                    input=request.stdin,
                    capture_output=True,
                    text=True,
                    timeout=self.TIMEOUT_SECONDS,
                    cwd=temp_path,
                    env=_sandbox_env(),
                )

                execution_time = (time.perf_counter() - execution_start) * 1000

                if execution.returncode != 0:
                    return CodeRunResponse(
                        status="runtime_error",
                        stdout=execution.stdout,
                        stderr=execution.stderr,
                        execution_time_ms=round(
                            execution_time,
                            2,
                        ),
                        memory_kb=None,
                    )

                return CodeRunResponse(
                    status="accepted",
                    stdout=execution.stdout,
                    stderr="",
                    execution_time_ms=round(
                        execution_time,
                        2,
                    ),
                    memory_kb=None,
                )

            except subprocess.TimeoutExpired:
                return CodeRunResponse(
                    status="time_limit_exceeded",
                    stdout="",
                    stderr="Time Limit Exceeded",
                    execution_time_ms=None,
                    memory_kb=None,
                )

            except Exception as exception:
                return CodeRunResponse(
                    status="internal_error",
                    stdout="",
                    stderr=str(exception),
                    execution_time_ms=None,
                    memory_kb=None,
                )

    def _run_sql(
        self,
        request: CodeRunRequest,
    ) -> CodeRunResponse:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            script_file = temp_path / "main.sql"
            db_file = temp_path / "main.db"

            script_file.write_text(
                request.code,
                encoding="utf-8",
            )

            start = time.perf_counter()

            try:
                # Each run gets a fresh on-disk SQLite database, so a
                # submission is expected to be self-contained (schema +
                # data + query), same as every other language here.
                # -header/-column give readable tabular output for SELECT
                # results; -bail stops at the first error instead of
                # limping through the rest of the script, matching how a
                # compiled/interpreted language run stops on its first
                # fatal error.
                execution = subprocess.run(
                    [
                        "sqlite3",
                        "-header",
                        "-column",
                        "-bail",
                        str(db_file),
                        f".read {script_file.name}",
                    ],
                    input=request.stdin,
                    capture_output=True,
                    text=True,
                    timeout=self.TIMEOUT_SECONDS,
                    cwd=temp_path,
                    env=_sandbox_env(),
                )

                execution_time = (time.perf_counter() - start) * 1000

                if execution.returncode != 0:
                    return CodeRunResponse(
                        status="runtime_error",
                        stdout=execution.stdout,
                        stderr=execution.stderr,
                        execution_time_ms=round(
                            execution_time,
                            2,
                        ),
                        memory_kb=None,
                    )

                return CodeRunResponse(
                    status="accepted",
                    stdout=execution.stdout,
                    stderr="",
                    execution_time_ms=round(
                        execution_time,
                        2,
                    ),
                    memory_kb=None,
                )

            except subprocess.TimeoutExpired:
                return CodeRunResponse(
                    status="time_limit_exceeded",
                    stdout="",
                    stderr="Time Limit Exceeded",
                    execution_time_ms=None,
                    memory_kb=None,
                )

            except Exception as exception:
                return CodeRunResponse(
                    status="internal_error",
                    stdout="",
                    stderr=str(exception),
                    execution_time_ms=None,
                    memory_kb=None,
                )

    def _not_implemented(
        self,
        language: str,
    ) -> CodeRunResponse:
        return CodeRunResponse(
            status="not_implemented",
            stdout="",
            stderr=f"{language} execution will be implemented next.",
        )

    def _run_c(
        self,
        request: CodeRunRequest,
    ) -> CodeRunResponse:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source_file = temp_path / "main.c"
            executable = temp_path / "main"

            source_file.write_text(
                request.code,
                encoding="utf-8",
            )

            compile_start = time.perf_counter()

            compile_process = subprocess.run(
                [
                    "gcc",
                    str(source_file),
                    "-O2",
                    "-o",
                    str(executable),
                ],
                capture_output=True,
                text=True,
                cwd=temp_path,
                env=_sandbox_env(),
            )

            if compile_process.returncode != 0:
                compile_time = (time.perf_counter() - compile_start) * 1000

                return CodeRunResponse(
                    status="compilation_error",
                    stdout="",
                    stderr=compile_process.stderr,
                    execution_time_ms=round(
                        compile_time,
                        2,
                    ),
                    memory_kb=None,
                )

            execution_start = time.perf_counter()

            try:
                execution = subprocess.run(
                    [str(executable)],
                    input=request.stdin,
                    capture_output=True,
                    text=True,
                    timeout=self.TIMEOUT_SECONDS,
                    cwd=temp_path,
                    env=_sandbox_env(),
                )

                execution_time = (time.perf_counter() - execution_start) * 1000

                if execution.returncode != 0:
                    return CodeRunResponse(
                        status="runtime_error",
                        stdout=execution.stdout,
                        stderr=execution.stderr,
                        execution_time_ms=round(
                            execution_time,
                            2,
                        ),
                        memory_kb=None,
                    )

                return CodeRunResponse(
                    status="accepted",
                    stdout=execution.stdout,
                    stderr="",
                    execution_time_ms=round(
                        execution_time,
                        2,
                    ),
                    memory_kb=None,
                )

            except subprocess.TimeoutExpired:
                return CodeRunResponse(
                    status="time_limit_exceeded",
                    stdout="",
                    stderr="Time Limit Exceeded",
                    execution_time_ms=None,
                    memory_kb=None,
                )

            except Exception as exception:
                return CodeRunResponse(
                    status="internal_error",
                    stdout="",
                    stderr=str(exception),
                    execution_time_ms=None,
                    memory_kb=None,
                )

    def _run_verilog(
        self,
        request: CodeRunRequest,
    ) -> CodeRunResponse:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source_file = temp_path / "main.v"
            executable = temp_path / "main.out"

            source_file.write_text(
                request.code,
                encoding="utf-8",
            )

            compile_start = time.perf_counter()

            compile_process = subprocess.run(
                [
                    "iverilog",
                    "-o",
                    str(executable),
                    str(source_file),
                ],
                capture_output=True,
                text=True,
                cwd=temp_path,
                env=_sandbox_env(),
            )

            if compile_process.returncode != 0:
                compile_time = (time.perf_counter() - compile_start) * 1000

                return CodeRunResponse(
                    status="compilation_error",
                    stdout="",
                    stderr=compile_process.stderr,
                    execution_time_ms=round(
                        compile_time,
                        2,
                    ),
                    memory_kb=None,
                )

            execution_start = time.perf_counter()

            try:
                execution = subprocess.run(
                    [
                        "vvp",
                        str(executable),
                    ],
                    input=request.stdin,
                    capture_output=True,
                    text=True,
                    timeout=self.TIMEOUT_SECONDS,
                    cwd=temp_path,
                    env=_sandbox_env(),
                )

                execution_time = (time.perf_counter() - execution_start) * 1000

                if execution.returncode != 0:
                    return CodeRunResponse(
                        status="runtime_error",
                        stdout=execution.stdout,
                        stderr=execution.stderr,
                        execution_time_ms=round(
                            execution_time,
                            2,
                        ),
                        memory_kb=None,
                    )

                return CodeRunResponse(
                    status="accepted",
                    stdout=execution.stdout,
                    stderr="",
                    execution_time_ms=round(
                        execution_time,
                        2,
                    ),
                    memory_kb=None,
                )

            except subprocess.TimeoutExpired:
                return CodeRunResponse(
                    status="time_limit_exceeded",
                    stdout="",
                    stderr="Time Limit Exceeded",
                    execution_time_ms=None,
                    memory_kb=None,
                )

            except Exception as exception:
                return CodeRunResponse(
                    status="internal_error",
                    stdout="",
                    stderr=str(exception),
                    execution_time_ms=None,
                    memory_kb=None,
                )
