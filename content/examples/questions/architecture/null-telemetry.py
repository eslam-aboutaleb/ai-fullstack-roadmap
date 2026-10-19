class NullTelemetry:
    def emit(self, event):
        pass
def run(telemetry):
    telemetry.emit({'event': 'started'})
    return 'completed'
print(run(NullTelemetry()))
