# Worker recovery

Worker leasing is deferred. When implemented, claiming, heartbeat, and final
status updates must use an ownership token and short transactions so a stale
worker cannot finalize a reassigned job.
