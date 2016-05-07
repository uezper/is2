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

Para ejecutar las pruebas unitarias usamos `python manage.py test DIRECCION_AL_DIRECTORIO"` donde DIRECCION_AL_DIRECTORIO es el camino al directorio donde residen los archivos con las pruebas. Los archivos deben tener el nombre de la forma `test_*.py` para ser detectados. Por ejemplo, 
```
python manager.py test apps/autenticacion/tests/
python manager.py test apps/administracion/tests/
```
Sería interesante poder usar un `script` para ejecutar todas las pruebas de una vez, sin embargo habría que leer si Django no posee esa funcionalidad.

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

user = User.users.create( **data ) # Para crear.
# users.get esta despreciado (:O) por users.filter, se va a terminar eliminando
result = User.users.get( 'johndoe1990' ) # Para obtener. Se estará extendiendo esto...
result.delete() # Para eliminar.
User.users.all() # Para listar.
User.users.filter(username='johndoe1990', ...) # Para hacer queries. Igual que con objects.filter
# Para users.filter se puede usar username, email, first_name, ..., telefono
```

Notar los ```**``` en las creaciones! Es para separar el proceso de ''construccion'' de los datos del proceso de ''creacion''. Tambien se puede hacer ```User.users.create(username='user', password='pass') # Y demas```. Con ```**``` se hacen lineas mas cortas, tambien.

Para roles y permisos

La creacion de un permiso se realiza utilizando el modelo de Django `django.auth.contrib.models.Permission` de la siguiente manera:

```python
  from django.auth.contrib.models import Permission
  from django.contrib.contenttypes.models import ContentType
  
  permission_data = {
          'name': 'Creacion de Sprints',                             # Descripcion larga del Permiso
          'codename': 'crear_sprint',                                # Nombre en codigo del Permiso
          'content_type': ContentType.objects.get_for_model(Project) # ContentType de algun modelo
  }
  
  perm = Permission.objects.create(**permission_data)

```
Sin embargo estos permisos deberian ser creados una sola vez. (Permisos por defecto del sistema)

Luego, para crear un rol, y teniendo en cuenta que la creacion de roles tendra sentido solo dentro del contexto de un proyecto, se realiza de la siguiente manera:

```python
  from apps.autenticacion.models import Role
  from apps.autenticacion.models import Project # Ubicacion temporal 
  
  role_data = {
    'name': 'scrum_master',         # Nombre en codigo del Rol
    'desc_larga': 'Scrum Master'     # Descripcion larga del Rol
  }
  
  # Crea el rol 'scrum_master' asociado al proyecto instanciado por p
  rol = p.add_rol(**role_data)      # p es una instancia de Project

```

Procedemos a agregar permisos al rol:

```python
  ...
  
  # Agrega el permiso 'crear_sprint' al rol 'scrum_master'
  rol.add_perm(perm)              # perm es una instancia de Permission

  ...
  
```

Ahora le asignamos el rol a un usuario y comprobamos si tiene un permiso dentro del proyecto. Para esto utilizamos
el nombre en codigo del permiso, de esta manera:

```python
  ...
  
  rol.add_user(user)            # user es una instancia de apps.autenticacion.models.User
  
  # Verificar si el usuario user tiene el permiso 'crear_sprint' dentro del proyecto p
  if p.has_perm(user, 'crear_sprint'):
    pass
  
  ...
  
```

### Sobre población de la base de datos
Ejecutar
```
python manager.py loaddata users.json    # Para agregar usuarios de autenticacion/fixtures/users.json
python manager.py loaddata projects.json # Para agregar projectos de administracion/fixtures/projects.json
python manager.py loadperms              # Para cargas los permisos por defecto
```
