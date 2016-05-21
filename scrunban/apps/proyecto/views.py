from apps.administracion.models import Project
from django.shortcuts import get_object_or_404

from apps.autenticacion.mixins import UserPermissionContextMixin
from scrunban.settings import base as base_settings

from django.shortcuts import render


def index(request, project_id):

    context = {
        'URL_NAMES': base_settings.URL_NAMES,
        'project' : get_object_or_404(Project, id=project_id)
    }
    import datetime
    now = datetime.datetime.now().date()
    if now < context['project'].date_start:
        context['project_state'] = 'Pendiente'
    elif context['project'].date_start < now < context['project'].date_end:
        context['project_state'] = 'Ejecutando'
    elif context['project'].date_end < now:
        context['project_state'] = 'Finalizado'
    x = UserPermissionContextMixin()
    x.project = context['project']
    x.request = request
    x.get_user_permissions_context(context)

    return render(request, 'proyecto/project_index', context)


