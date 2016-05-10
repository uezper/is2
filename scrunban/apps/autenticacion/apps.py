from django.apps import AppConfig

class AutenticacionConfig(AppConfig):
    name = 'apps.autenticacion'

    # Llamar a este metodo para poblar la base de datos con los permisos por defecto del sistema
    # Pero antes deben estar aplicado las migraciones
    def get_ready(self):
        from apps.autenticacion.models import Role, User
        from apps.autenticacion import settings
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        __user_contenttype = ContentType.objects.get_for_model(User)

        for def_perm in settings.DEFAULT_PERMISSIONS:
            perm = Permission.objects.filter(codename=def_perm[0])
            if (len(perm) == 0):
                permission_data = {
                    'name': def_perm[1],
                    'codename': def_perm[0],
                    'content_type': __user_contenttype
                }
                perm = Permission.objects.create(**permission_data)

        for def_rol in settings.DEFAULT_ADMIN_ROLES:
            rol = Role.roles.filter(name=def_rol[0])
            if (len(rol) == 0):
                print('Creando rol ' + def_rol[0])
                role_data = {
                    'name': def_rol[0],
                    'desc_larga': def_rol[1]
                }
                r = Role.roles.create(**role_data)

                for p in def_rol[2]:
                    perm = Permission.objects.filter(codename=p[0])[0]
                    r.add_perm(perm)

