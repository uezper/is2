from django import forms

class ProjectForm(forms.Form):
    nombre = forms.CharField(label = "Nombre del Proyecto", max_length=128)
    fechaInicio = forms.DateField(label = "Inicio")
    fechaFinal = forms.DateField(label = "Fin")
    scrumMaster = forms.CharField(label = "Scrum Master", max_length = 128)
    productOwner = forms.CharField(label = "Product Owner", max_length = 128)

 
