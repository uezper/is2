from apps.administracion.models import Project
from django.shortcuts import get_object_or_404
from apps.autenticacion.mixins import UserPermissionContextMixin
from scrunban.settings import base as base_settings

from django.shortcuts import render


def index(request, project_id):

    context = {
        'URL_NAMES': base_settings.URL_NAMES,
        'project': get_object_or_404(Project, id=project_id),
        'section_title': 'Estado',
        'left_active': 'Estado'
    }
    context['project_state'] = context['project'].get_state()
    x = UserPermissionContextMixin()
    x.project = context['project']
    x.request = request
    x.get_user_permissions_context(context)

    return render(request, 'proyecto/project_state', context)


#@login_required()
def burndown_chart(request, project_id):
    context = {
        'URL_NAMES': base_settings.URL_NAMES,
        'project': get_object_or_404(Project, id=project_id),
        'section_title':'Burndown Chart',
        'left_active':'Burndown'
    }
    return render(request, 'proyecto/burndown_chart/base', context)