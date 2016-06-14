from django import forms
from django.forms import ModelForm, Textarea
from django.core.exceptions import ValidationError
from apps.administracion.models import Flow, UserStory, UserStoryType, Project
from apps.autenticacion.models import User
from django.forms import ModelForm

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'scrum_master', 'product_owner']

class UserForm(forms.Form):
    id = forms.CharField(max_length=4,widget=forms.HiddenInput, required=False)
    username = forms.CharField(max_length=128,widget=forms.HiddenInput, required=False)
    password = forms.CharField(max_length=128,widget=forms.HiddenInput, required=False)
    first_name = forms.CharField(max_length=128, widget=forms.HiddenInput, required=False)
    last_name = forms.CharField(max_length=128, widget=forms.HiddenInput, required=False)
    direccion = forms.CharField(max_length=128, widget=forms.HiddenInput, required=False)
    telefono = forms.CharField(max_length=128, widget=forms.HiddenInput, required=False)
    email = forms.CharField(max_length=128, widget=forms.HiddenInput, required=False)

    def clean_username(self):
        if not(self.cleaned_data['username'] == ''):
            if not(self.cleaned_data['username'].isdigit()):
                raise ValidationError('Este campo solo puede contener numeros')

        return self.cleaned_data['username']

class UserCreateForm(UserForm):

    username = forms.CharField(max_length=128, required=True, widget=forms.HiddenInput)
    password = forms.CharField(max_length=128, required=True, widget=forms.HiddenInput)

    def clean_username(self):

        if len(User.users.filter(username=self.cleaned_data['username'])) != 0:
            raise ValidationError('El usuario ya existe')

        return self.cleaned_data['username']

    def save(self):

        data = {
            'username' : self.cleaned_data['username'],
            'password' : self.cleaned_data['password'],
            'direccion' : self.cleaned_data.get('direccion', ''),
            'email': self.cleaned_data.get('email', ''),
            'telefono': self.cleaned_data.get('telefono', ''),
            'first_name': self.cleaned_data.get('first_name', ''),
            'last_name': self.cleaned_data.get('last_name', '')
        }


        User.users.create(**data)


class UserEditForm(UserForm):
    id = forms.CharField(max_length=4, required=True, widget=forms.HiddenInput)
    check_password = forms.CharField(max_length=128, required=False, widget=forms.HiddenInput)


    def clean_id(self):
        if len(User.objects.filter(id=self.cleaned_data['id'])) == 0:
            raise ValidationError('El usuario especificado no existe')
        return self.cleaned_data['id']

    def clean_check_password(self):

        if self.cleaned_data.get('password','') != '' and self.cleaned_data.get('password','') != self.cleaned_data['check_password']:
            raise ValidationError('Ambos campos deben coincidir')
        return self.cleaned_data['check_password']

    def clean_username(self):
        return self.cleaned_data['username']

    def save(self):
        data = {
            'email': self.cleaned_data.get('email', ''),
            'first_name': self.cleaned_data.get('first_name', ''),
            'last_name': self.cleaned_data.get('last_name', ''),
            'direccion': self.cleaned_data.get('direccion', ''),
            'telefono': self.cleaned_data.get('telefono', ''),
            'password': self.cleaned_data.get('password', '')
        }

        user = User.objects.filter(id=self.cleaned_data['id'])[0]

        if (data['email'] != ''):
            user.set_email(data['email'])

        if (data['first_name'] != ''):
            user.set_first_name(data['first_name'])

        if (data['last_name'] != ''):
            user.set_last_name(data['last_name'])

        if (data['direccion'] != ''):
            user.set_direccion(data['direccion'])

        if (data['telefono'] != ''):
            user.set_telefono(data['telefono'])

        if (data['password'] != ''):
            user.user.set_password(data['password'])

        user.user.save()
        user.save()


class UserDeleteForm(UserForm):
    id = forms.CharField(max_length=4, required=True, widget=forms.HiddenInput)

    def clean_id(self):

        if len(User.objects.filter(id=self.cleaned_data['id'])) == 0:
            raise ValidationError('El usuario especificado no existe')
        return self.cleaned_data['id']


    def save(self):
        u = User.objects.filter(id=self.cleaned_data['id'])[0]
        #u.delete()
        x = u.user
        x.is_active = False
        x.save()


class FlowForm(ModelForm):
    class Meta():
        model=Flow
        fields=['name']

class UserStoryForm(ModelForm):
    def __init__(self, project, *args, **kwargs):
        from apps.administracion.models import UserStoryType
        super(UserStoryForm, self).__init__(*args, **kwargs)
        self._project = project
        # Add Tipo de User Story field
        self.choices = []
        for typeUs in UserStoryType.objects.filter(project=project):
            self.choices.append((typeUs.id, typeUs.name))
        self.choices = tuple(self.choices)
        self.fields['us_type_'] = forms.ChoiceField(
            label='Tipo de User Story',
            widget=forms.RadioSelect,
            choices=self.choices
        )
        # Personalize fields
        fields_names = [
            'description', 'details', 'acceptance_requirements', 'estimated_time',
            'business_value', 'tecnical_value', 'urgency'    
        ]
        for field_name in fields_names:
            field = self.fields.get(field_name, 'False')
            if field:
                field.widget.attrs['class'] = 'form-control'

    def clean_description(self):
        cleaned_description = self.cleaned_data.get('description', '')
        descriptions = [us.description for us in UserStory.user_stories.filter(project=self._project)]

        if cleaned_description in descriptions:
            raise ValidationError('Descripcion ya existente en el proyecto.')
        
        return cleaned_description
        
    class Meta():
        model=UserStory
        fields=[
            'description', 'details', 'acceptance_requirements', 'estimated_time',
            'business_value', 'tecnical_value', 'urgency'    
        ]
        widgets = {
            'details': Textarea({'cols':100, 'rows':4}),
            'acceptance_requirements': Textarea({'cols':100, 'rows':4}),
            
        }

class UserStoryTypeForm(ModelForm):
    def __init__(self, project, *args, **kwargs):
        super(UserStoryTypeForm, self).__init__(*args, **kwargs)
        self._project = project
        # Add Flujos field
        self.choices = []
        for flow in Flow.flows.filter(project=project):
            self.choices.append( (flow.pk, flow.name) )
        self.choices = tuple( self.choices )

        self.fields['flows'] = forms.MultipleChoiceField(
            label='Flujos',
            widget=forms.CheckboxSelectMultiple,
            choices=self.choices
        )
        # Personalize fields
        name_field = self.fields.get('name', False)
        if name_field:
            name_field.widget.attrs['class'] = 'form-control'

    def clean_name(self):
        cleaned_name = self.cleaned_data.get('name', '')
        names = [ust.name for ust in UserStoryType.types.filter(project=self._project)]

        if cleaned_name in names:
            raise ValidationError('Nombre ya existente en el proyecto.')

        return cleaned_name
        
    class Meta:
        model = UserStoryType
        fields = ['name']
