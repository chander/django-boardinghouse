"""
:mod:`boardinghouse.management.commands.loaddata`

This replaces the ``loaddata`` command with one that takes a new
option: ``--schema``. This is required when non-shared-models are
included in the file(s) to be loaded, and the schema with this name
will be used as a target.
"""
from django.core.management.commands import loaddata

from ...schema import activate_schema, deactivate_schema


class Command(loaddata.Command):
    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--schema', action='store', dest='schema',
            help='Specify which schema to load schema-aware models to')

    def handle(self, *fixture_labels, **options):
        schema_name = options.get('schema')
        if schema_name:
            activate_schema(schema_name)

        # We should wrap this in a try/except, and present a reasonable
        # error message if we think we tried to load data without a schema
        # that required one.
        super(Command, self).handle(*fixture_labels, **options)

        if schema_name:
            deactivate_schema()
