from django.apps import AppConfig

class AutenticacionConfig(AppConfig):
    name = 'apps.autenticacion'

    def ready(self):
        from apps.autenticacion.models import Role
        from apps.autenticacion import settings
        from django.contrib.auth.models import Permission

        for def_perm in settings.DEFAULT_PERMISSIONS:
            perm = Permission.objects.filter(codename=def_perm[0])
            if (len(perm) == 0):
                permission_data = {
                    'name': def_perm[1],
                    'codename': def_perm[0],
                    'content_type': def_perm[2]
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

