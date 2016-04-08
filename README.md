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

Se puede guardar en un archivo.txt y luego ejecutar:

```
$ pip install -r < archivo.txt
```

### Documentacion

Para crear la documentacion, luego de haber instalado las dependencias, en /docs/

```
$ make html
```
Los archivos generados van a /docs/build/

### Configuracion

La configuracion esta dividida en 4 archivos, todos incluidos en settings/

```
base.py
dev.py
prod.py
secret_config.py
```

base.py: Contiene configuracion comun a los ambientes de desarrollo y produccion
dev.py: Contiene configuracion especifica del ambiente de desarrollo
prod.py: Contiene configuracion especifica del ambiente de produccion
secret_config.py: Contiene configuracion sensible, datos privados y que no deberian ser publicados por lo cual no es compartida en el repositorio.

Si bien el archivo `secret_config.py` no se encuentra en el repositorio, es indispensable para que la aplicacion corra. Un ejemplo de configuracion seria:

```
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'CLAVE SECRETA GENERADA POR DJANGO'

DB_USER = 'TU USUARIO';
DB_PASSWORD = 'TU PASSWORD';
DB_DATABASE = 'EL NOMBRE DE TU BD';
```
