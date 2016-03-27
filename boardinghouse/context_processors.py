from __future__ import unicode_literals

from django.utils.translation import ugettext as _

from .schema import get_schema_model


def schemata(request):
    """
    A Django context_processor that provides access to the
    logged-in user's visible schemata, and selected schema.

    Adds the following variables to the context:

        `schemata`: all available schemata this user has

        `selected_schema`: the currenly selected schema name

    """
    if request.user.is_anonymous():
        return {}

    extra_schemata = None

    if request.user.is_staff or request.user.is_superuser:
        available_schemata = get_schema_model().objects.all()
        # Only if templates are installed.
        try:
            from boardinghouse.contrib.template.models import SchemaTemplate
        except ImportError:
            pass
        else:
            extra_schemata = [(_('Templates'), SchemaTemplate.objects.all())]
    else:
        available_schemata = request.user.visible_schemata

    return {
        'schemata': available_schemata,
        'selected_schema': request.session.get('schema', None),
        'extra_schemata': extra_schemata
    }
