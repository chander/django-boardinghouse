SHARED_MODELS = []
"""
Models that should be in the public/shared schema,
rather than in each tenant's schema.

Note that some models are *always* shared, which you
can see in :attr:`boardinghouse.schema.REQUIRED_SHARED_MODELS`
"""

PRIVATE_MODELS = []
"""
Overrides for models that should be place in each schema.

This enables us to do magic like have the m2m join table for a pair
of shared models be schema-aware.

Can we annotate a ForeignKey field, or perhaps do something in the
Model.Meta to set this?

Perhaps we could have a SchemaAwareManyToManyField()...
"""

PUBLIC_SCHEMA = 'public'
"""
The name of the public schema. The default should work for all cases,
other than where you know you need to change it.
"""

TEMPLATE_SCHEMA = '__template__'
"""
The name of the template schema. The default should probably be okay, but
if you really know that it needs to change, then you may.
"""

BOARDINGHOUSE_SCHEMA_MODEL = 'boardinghouse.Schema'
"""
The model that will store the actual schema objects. This should be a
subclass of :class:`boardinghouse.models.AbstractSchema`, or expose the
same methods.
"""
