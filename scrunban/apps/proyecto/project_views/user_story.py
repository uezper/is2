from django.shortcuts import get_object_or_404
from django.views.generic import FormView
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http.response import HttpResponseRedirect

from apps.proyecto.mixins import ProjectViwMixin, DefaultFormDataMixin
from apps.proyecto import forms
from apps.administracion.models import UserStory


class UserStorySummaryView(ProjectViwMixin, DefaultFormDataMixin, FormView):
    """
        Clase correspondiente a la vista que muestra la informacion sobre un User Story dentor de un proyecto

        :param form_class: Formulario que se encarga de la validacion de los datos ingresados por usuarios
        :param template_name: Nombre del template que sera utilizado
        :param pk_url_kwarg: Nombre del parametro de url que contiene el id del proyecto
        :param us_url_kwarg: Nombre del parametro url que contiene el id del user story
        :param section_title: Titulo de la Seccion, colocado dentro del context['section_title']
        :param left_active: Nombre de la seccion activa del menu lateral izquierdo
        :param notes_paginate_by: Nro. maximo de notas por pagina
        :param notes_paginate_name: Nombre del parametro url de la pagina actual de notas

        Esta clase hereda de `ProjectViewMixin`, `DefaultFormDataMixin` y de `FormView`
        """

    form_class = forms.AproveNoteForm
    template_name = 'proyecto/project_userstory_summary'
    pk_url_kwarg = 'project_id'
    us_url_kwarg = 'user_story_id'
    notes_paginate_by = 10
    section_title = 'Detalles del User Story'
    left_active = 'User Stories'
    notes_page_name = 'notes_page'

    def validate_tests(self, request, *args, **kwargs):
        """
        Metodo que se encarga de validar que se cumpla una condicion para entrar a la vista

        :return:  Url a donde sera redirigido si el test falla, o None
        """
        from django.contrib.auth.models import Permission
        from apps.autenticacion.settings import PROJECT_US_DEVELOP, PROJECT_US_MANAGEMENT, PROJECT_US_APROVE, PROJECT_PB_WATCH, PROJECT_SPRINT_MANAGEMENT

        us = get_object_or_404(UserStory, id=kwargs.get(self.us_url_kwarg, ''))

        user_perms = self.get_user_permissions_list()

        permissions = [
            PROJECT_PB_WATCH,
            PROJECT_SPRINT_MANAGEMENT,
            PROJECT_US_APROVE,
            PROJECT_US_MANAGEMENT,
            PROJECT_US_DEVELOP
        ]
        permissions = [Permission.objects.get(codename=p[0]) for p in permissions]


        # Verifica que al menos tenga uno de los permisos en 'permissions'

        pass_test = False
        for perm in permissions:
            if perm in user_perms:
                pass_test = True


        if pass_test:
            return None

        return self.get_fail_permission_url(request, *args, **kwargs)


    def get_default_fields(self):
        """
            Campos por defecto que son agregados a los datos proveidos por los usuarios al enviar un formulario.

            :return: Diccionario con campos por defectos y sus respectivos valores.
            """
        project = self.get_project()
        user = self.request.user.user

        initial = {
            'project_id': project.id,
            'user_id': user.id
        }

        return initial

    def get_context_data(self, **kwargs):
        """
            Metodo que retorna el context que sera enviado al template

            :return: Context
            """
        context = super(UserStorySummaryView, self).get_context_data(**kwargs)
        self.user_story = get_object_or_404(UserStory, id=self.kwargs.get(self.us_url_kwarg, ''))

        state_str = ['Pendiente', 'Ejecutando', 'Finalizado']

        context['user_story'] = self.user_story
        context['user_story'].state = state_str[context['user_story'].state]
        context['user_story_data'] = self.get_context_us_data()

        return context

    def get_context_us_data(self):
        """
        Agrega informacion adicional al context

        :return: Informacion adicional a ser agregada al context
        """
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
        """
            Metodo que es llamado cuando un formulario enviado por el usuario es valido.

            :param form: Formulario que ha sido ya comprobado y es valido
            :return: HttpResponse
            """
        context = {}
        form.save()
        return super(UserStorySummaryView, self).render_to_response(self.get_context_data(**context))

    def form_invalid(self, form):
        """
            Netodo que es llamado cuando un formulario enviado por el usuario es invalido.

            :param form: Formulario invalido con los errores respectivos
            :return: HttpResponse
            """
        context = {
            'form': form
        }

        return super(UserStorySummaryView, self).render_to_response(self.get_context_data(**context))



class UserStoryAddWorkload(ProjectViwMixin, DefaultFormDataMixin, FormView):
    """
        Clase correspondiente a la vista que muestra la informacion sobre un User Story dentor de un proyecto

        :param form_class: Formulario que se encarga de la validacion de los datos ingresados por usuarios
        :param template_name: Nombre del template que sera utilizado
        :param pk_url_kwarg: Nombre del parametro de url que contiene el id del proyecto
        :param us_url_kwarg: Nombre del parametro url que contiene el id del user story
        :param section_title: Titulo de la Seccion, colocado dentro del context['section_title']
        :param left_active: Nombre de la seccion activa del menu lateral izquierdo

        Esta clase hereda de `ProjectViewMixin`, `DefaultFormDataMixin` y de `FormView`
        """

    form_class = forms.AddWorkLoad
    template_name = 'proyecto/project_userstory_addwork'
    pk_url_kwarg = 'project_id'
    us_url_kwarg = 'user_story_id'
    section_title = 'Agregar trabajo al User Story'
    left_active = 'User Stories'

    def validate_tests(self, request, *args, **kwargs):
        """
        Metodo que se encarga de validar que se cumpla una condicion para entrar a la vista

        :return:  Url a donde sera redirigido si el test falla, o None
        """
        from apps.proyecto.models import Sprint
        from apps.administracion.models import Grained
        from django.contrib.auth.models import Permission
        from apps.autenticacion.settings import PROJECT_US_DEVELOP
        from scrunban.settings.base import PROJECT_INDEX, PROJECT_SPRINT_KANBAN

        project = self.get_project()
        project_index = reverse(PROJECT_INDEX, args=(project.id,))

        us = get_object_or_404(UserStory, id=kwargs.get(self.us_url_kwarg, ''))

        user = self.request.user.user
        user_perms = self.get_user_permissions_list()

        if us.state != 1:
            return project_index

        if not Permission.objects.get(codename=PROJECT_US_DEVELOP[0]) in user_perms:
            return project_index

        sprint = Sprint.objects.filter(project=project, state='Ejecucion')
        if len(sprint) == 0:
            return project_index

        sprint = sprint[0]
        grained = Grained.objects.filter(user_story=us, sprint=sprint)

        if len(grained) == 0:
            return project_index

        grained = grained[0]
        developers = [t.user for t in grained.developers.all()]

        if not(user in developers):
            return reverse(PROJECT_SPRINT_KANBAN, args=(project.id, sprint.id))

        return None


    def get_default_fields(self):
        """
            Campos por defecto que son agregados a los datos proveidos por los usuarios al enviar un formulario.

            :return: Diccionario con campos por defectos y sus respectivos valores.
            """
        from apps.administracion.models import Grained
        from apps.proyecto.models import Sprint
        us = get_object_or_404(UserStory, id=self.kwargs.get(self.us_url_kwarg, ''))
        project = self.get_project()
        sprint = Sprint.objects.get(project=project, state='Ejecucion')

        grained = Grained.objects.get(user_story=us, sprint=sprint)

        user = self.request.user.user

        initial = {
            'user': user.id,
            'grained': grained.id
        }

        return initial

    def get_context_data(self, **kwargs):
        """
            Metodo que retorna el context que sera enviado al template

            :return: Context
            """
        context = super(UserStoryAddWorkload, self).get_context_data(**kwargs)
        self.user_story = get_object_or_404(UserStory, id=self.kwargs.get(self.us_url_kwarg, ''))

        context['user_story'] = self.user_story

        return context


    def get_success_url(self):
        """
            Retorna la url a donde sera redirigido el usuario cuando se haya procesado correctamente un formulario

            :return: Url
            """
        from apps.proyecto.models import Sprint
        from scrunban.settings.base import PROJECT_SPRINT_KANBAN
        project = self.get_project()
        sprint = Sprint.objects.get(project=project, state='Ejecucion')

        return reverse(PROJECT_SPRINT_KANBAN, args=(project.id, sprint.id))


    def form_valid(self, form):
        """
            Metodo que es llamado cuando un formulario enviado por el usuario es valido.

            :param form: Formulario que ha sido ya comprobado y es valido
            :return: HttpResponse
            """
        form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        """
            Netodo que es llamado cuando un formulario enviado por el usuario es invalido.

            :param form: Formulario invalido con los errores respectivos
            :return: HttpResponse
            """
        context = {
            'form': form
        }
        return super(UserStoryAddWorkload, self).render_to_response(self.get_context_data(**context))
