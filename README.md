# Proyecto de Ingeniería de Software 2
## Sistema de Administración de Proyectos - Sirentos/Scrumban?

### Datos
Requerimientos:

```
alabaster==0.7.7
Babel==2.3.1
Django==1.9.5
django-guardian==1.4.2
docutils==0.12
imagesize==0.7.0
Jinja2==2.8
MarkupSafe==0.23
Pygments==2.1.3
pytz==2016.3
six==1.10.0
snowballstemmer==1.2.1
Sphinx==1.4
```

Se puede guardar en un `archivo.txt` y luego ejecutar por medio de la terminal:

```
$ pip install -r < archivo.txt
```

De esta manera, instalar todos los requerimientos necesarios

### Documentación

Para crear la documentación, luego de haber instalado las dependencias. Ve a /docs/ y ejecuta:

```
$ make html
```
Los archivos generados van a /docs/build/

### Configuración

La configuración esta dividida en 4 archivos, todos incluidos en settings/

- `base.py`: Contiene configuración comun a los ambientes de desarrollo y produccion
- `dev.py`: Contiene configuración especifica del ambiente de desarrollo
- `prod.py`: Contiene configuración especifica del ambiente de produccion
- `secret_config.py`: Contiene configuración sensible, datos privados y que no deberian ser publicados por lo cual no es compartida en el repositorio.

Si bien el archivo `secret_config.py` no se encuentra en el repositorio, es fundamental para que la aplicacion corra. Un ejemplo de configuracion seria:

```
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'CLAVE SECRETA GENERADA POR DJANGO'

DB_USER = 'TU USUARIO';
DB_PASSWORD = 'TU PASSWORD';
DB_DATABASE = 'EL NOMBRE DE TU BD';

```
### Test Unitarios
Para ejecutar los tests unitarios, se debe ejecutar "./manage.py test"

### Sobre modelos
Para usuario:

```python
data = {
'username'  : 'johndoe1990',
'password'  : 'weak_password',
'email'     : 'jdoe@somewhere.com',
'first_name': 'John',
'last_name' : 'Doe',
'direccion' : 'Somewhere',
'telefono'  : '1234567890'
}

user = User.objects.create( **data ) # Para crear.
result = User.objects.get( 'johndoe1990' ) # Para obtener.
result.delete() # Para eliminar.

```

Para permisos:

```python
data = {
'codename'  : 'perm1',
'name'      : 'Permiso 1',
'desc_larga': 'Permiso creado para pruebas!',
}

perm = Permission.objects.create( **data ) # Para crear.
# Falta implementar busqueda.. ^_^
perm.delete() # Para eliminar

```

Notar los ```**``` en las creaciones!