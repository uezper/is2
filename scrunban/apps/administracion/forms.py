from django import forms

class ProjectForm(forms.Form):
    name = forms.CharField(label = "Nombre del Proyecto", max_length=128)
    date_start = forms.DateField(label = "Fecha de inicio")
    date_end = forms.DateField(label = "Fecha de finalizacion")
    scrum_master = forms.CharField(label = "Scrum Master", max_length = 128)
    product_owner = forms.CharField(label = "Product Owner", max_length = 128)

 
