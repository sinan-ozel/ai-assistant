"""Supervisord event listener: shut the container down when fastapi exits.

Listens for PROCESS_STATE_EXITED and PROCESS_STATE_FATAL events.  When the
fastapi program exits with a non-zero code (or goes FATAL), writes
/tmp/fatal-error so entrypoint.sh propagates exit code 1 to Docker /
Kubernetes.  Then signals supervisord to shut down and blocks — supervisord
will kill this process as part of its graceful shutdown sequence.
"""

import os
import signal
import sys
import time


def _write_fatal_sentinel():
    try:
        open("/tmp/fatal-error", "w").close()
    except OSError:
        pass


def _supervisord_pid() -> int:
    with open("/var/run/supervisord.pid") as f:
        return int(f.read().strip())


def main():
    while True:
        sys.stdout.write("READY\n")
        sys.stdout.flush()

        header_line = sys.stdin.readline()
        headers = {}
        for token in header_line.split():
            if ":" in token:
                k, v = token.split(":", 1)
                headers[k] = v

        data_len = int(headers.get("len", 0))
        data = sys.stdin.read(data_len) if data_len else ""

        event_data = {}
        for token in data.split():
            if ":" in token:
                k, v = token.split(":", 1)
                event_data[k] = v

        if event_data.get("processname") == "fastapi":
            event_name = headers.get("eventname", "")
            if event_name == "PROCESS_STATE_FATAL":
                _write_fatal_sentinel()
            else:
                try:
                    exit_code = int(event_data.get("exitcode", "1"))
                except ValueError:
                    exit_code = 1
                if exit_code != 0:
                    _write_fatal_sentinel()

            # Acknowledge the event before shutting down.
            sys.stdout.write("RESULT 2\nOK")
            sys.stdout.flush()

            # Signal supervisord to shut down gracefully.  Block here so we
            # never write another READY — supervisord will kill this process
            # during its shutdown sequence.
            os.kill(_supervisord_pid(), signal.SIGTERM)
            while True:
                time.sleep(1)

        sys.stdout.write("RESULT 2\nOK")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
