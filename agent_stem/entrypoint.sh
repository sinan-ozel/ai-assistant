#!/bin/sh
# Remove any stale sentinel from a previous run.
rm -f /tmp/fatal-error

supervisord -c /etc/supervisor/conf.d/supervisord.conf

# supervisord exited (via SIGTERM from api.py on a fatal startup error, or a
# normal docker stop).  If api.py wrote the sentinel first, surface exit code 1
# so Kubernetes reports "Reason: Error" rather than "Reason: Completed".
if [ -f /tmp/fatal-error ]; then
    exit 1
fi
exit 0
