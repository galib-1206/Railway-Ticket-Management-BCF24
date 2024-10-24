# opentelemetry_django.py

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.django import DjangoInstrumentor

def init_tracer (service_name):
    resource=Resource({"service.name": service_name})
# Set the tracer provider
trace.set_tracer_provider(TracerProvider())

# Configure the Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",  # Change this if Jaeger is hosted elsewhere
    agent_port=6831,              # Default Jaeger UDP port
)

# Add the exporter to the tracer provider
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Instrument Django with OpenTelemetry
DjangoInstrumentor().instrument()


