"""Actual Beam DirectRunner pipeline with event time, late panes and aggregation.

Requires requirements-advanced.txt. TestStream advances a synthetic watermark;
this is not a Kafka broker or a production distributed runner.
"""
import json
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.test_stream import TestStream
from apache_beam.testing.util import assert_that, equal_to
from apache_beam.transforms import trigger, window


def verify():
    options = PipelineOptions(['--runner=DirectRunner'])
    options.view_as(StandardOptions).streaming = True
    stream = (TestStream().advance_watermark_to(0)
        .add_elements([window.TimestampedValue(('tenant-a',2),1), window.TimestampedValue(('tenant-a',3),2)])
        .advance_watermark_to(12)
        .add_elements([window.TimestampedValue(('tenant-a',7),3)])
        .advance_watermark_to(25)
        .add_elements([window.TimestampedValue(('tenant-a',100),4)])
        .advance_watermark_to_infinity())
    with TestPipeline(options=options) as pipeline:
        totals = (pipeline | stream
            | beam.WindowInto(window.FixedWindows(10), trigger=trigger.AfterWatermark(late=trigger.AfterCount(1)),
                accumulation_mode=trigger.AccumulationMode.ACCUMULATING, allowed_lateness=10)
            | beam.CombinePerKey(sum)
            | beam.Map(lambda pair: pair[1]))
        # First pane is 5; accepted late event corrects it to 12. The element
        # after window end+allowed lateness must not produce a 112 correction.
        assert_that(totals, equal_to([5,12]))
    print(json.dumps({'runner':'Beam DirectRunner','on_time_total':5,'late_correction':12,
                      'beyond_lateness_event':'discarded','accumulation':'accumulating'}))


if __name__ == '__main__':
    verify()
