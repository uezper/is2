from django.shortcuts import get_object_or_404
from django.views.generic import FormView
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http.response import HttpResponseRedirect

from apps.proyecto.mixins import ProjectViwMixin, DefaultFormData
from apps.proyecto import forms
from apps.administracion.models import UserStory


class UserStorySummaryView(ProjectViwMixin, DefaultFormData, FormView):

    """
    Clase correspondiente a la vista que muestra la informacion sobre un User Story de un proyecto

    """

    form_class = forms.AproveUSForm
    template_name = 'proyecto/project_user_story_summary'
    pk_url_kwarg = 'project_id'
    us_url_kwarg = 'user_story_id'
    notes_paginate_by = 10
    section_title = 'Detalles del User Story'
    left_active = 'User Stories'
    notes_page_name = 'notes_page'

    def get_default_fields(self):
        project = self.get_project()
        user = self.request.user.user

        initial = {
            'project_id': project.id,
            'user_id': user.id
        }

        return initial

    def get_context_data(self, **kwargs):
        context = super(UserStorySummaryView, self).get_context_data(**kwargs)
        self.user_story = get_object_or_404(UserStory, id=self.kwargs.get(self.us_url_kwarg, ''))

        state_str = ['Pendiente', 'Ejecutando', 'Finalizado']

        context['user_story'] = self.user_story
        context['user_story'].state = state_str[context['user_story'].state]
        context['user_story_data'] = self.get_context_us_data()

        return context

    def get_context_us_data(self):
        from apps.administracion.models import Grained, Note

        notes = []
        for g in Grained.objects.filter(user_story=self.user_story).order_by('-id'):
            for n in Note.objects.filter(grained=g).order_by('-date'):
                notes.append(n)

        # Paginacion

        notes_paginator = Paginator(notes, self.notes_paginate_by)
        notes_page = self.request.GET.get(self.notes_page_name, 1)
        try:
            notes_paginated = notes_paginator.page(notes_page)
        except PageNotAnInteger:
            notes_paginated = notes_paginator.page(1)
        except EmptyPage:
            notes_paginated = notes_paginator.page(notes_paginator.num_pages)


        # Prepara el context

        us_data = {}
        us_data['note_list'] = notes_paginated

        return us_data

    def form_valid(self, form):
        context = {}
        form.save()
        return super(UserStorySummaryView, self).render_to_response(self.get_context_data(**context))

    def form_invalid(self, form):

        context = {
            'form': form
        }

        return super(UserStorySummaryView, self).render_to_response(self.get_context_data(**context))
