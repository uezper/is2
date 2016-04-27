from django.contrib.contenttypes.models import ContentType
from apps.autenticacion.models import User, Project

__user_contenttype = ContentType.objects.get_for_model(User)
__project_contenttype = ContentType.objects.get_for_model(Project)

ADMIN_PROJECT_CREATION = ('admin_create_project', 'Creacion de proyectos', __user_contenttype)
ADMIN_ROLE_MANAGEMENT = ('admin_create_admin', 'Asignacion de roles administrativos', __user_contenttype)
ADMIN_USER_MANAGEMENT = ('admin_manage_user', 'Administracion de usuarios', __user_contenttype)
PROJECT_ROL_MANAGEMENT = ('project_rol_management', 'Creacion y modificacion de roles de proyecto',__project_contenttype)
PROJECT_ROL_ASSIGNMENT = ('project_rol_assignment', 'Asignacion de roles de proyectos',__project_contenttype)
PROJECT_FLUJO_MANAGEMENT = ('project_flujo_management', 'Administracion de Flujos',__project_contenttype)
PROJECT_FLUJO_WATCH = ('project_flujo_watch', 'Visualizacion de Flujos',__project_contenttype)
PROJECT_DEV_MANAGEMENT = ('project_dev_management', 'Administracion de Equipo de Desarrollo',__project_contenttype)
PROJECT_SPRINT_MANAGEMENT = ('project_sprint_management', 'Administracion de Sprints',__project_contenttype)
PROJECT_TUS_MANAGEMENET = ('project_tus_management', 'Administracion de Flujos de User Stories',__project_contenttype)
PROJECT_INFO_MANAGEMENT = ('project_info_management', 'Administracion del Proyecto',__project_contenttype)
PROJECT_US_MANAGEMENT = ('project_us_management', 'Administracion de User Stories',__project_contenttype)
PROJECT_US_DEVELOP = ('project_us_develop', 'Desarrollo de User Stories',__project_contenttype)
PROJECT_KANBAN_WATCH = ('project_kanban_watch', 'Visualizacion del Kanban',__project_contenttype)
PROJECT_PB_WATCH = ('project_pb_watch', 'Visualizacion del Product Backlog',__project_contenttype)
PROJECT_SB_WATCH = ('project_sb_watch', 'Visualizacion del Sprint Backlog',__project_contenttype)


DEFAULT_PERMISSIONS = [
    ADMIN_PROJECT_CREATION,
    ADMIN_ROLE_MANAGEMENT,
    ADMIN_USER_MANAGEMENT,
    PROJECT_ROL_MANAGEMENT,
    PROJECT_ROL_ASSIGNMENT,
    PROJECT_FLUJO_MANAGEMENT,
    PROJECT_FLUJO_WATCH,
    PROJECT_DEV_MANAGEMENT,
    PROJECT_SPRINT_MANAGEMENT,
    PROJECT_TUS_MANAGEMENET,
    PROJECT_INFO_MANAGEMENT,
    PROJECT_US_MANAGEMENT,
    PROJECT_US_DEVELOP,
    PROJECT_KANBAN_WATCH,
    PROJECT_PB_WATCH,
    PROJECT_SB_WATCH,
]

DEF_ROLE_ADMIN = ('system_admin', 'Administrador del Sistema',
                  [
                      ADMIN_PROJECT_CREATION,
                      ADMIN_ROLE_MANAGEMENT,
                      ADMIN_USER_MANAGEMENT
                  ])

DEF_ROLE_SCRUM_MASTER = ('scrum_master','Scrum Master',
                         [
                             PROJECT_ROL_MANAGEMENT,
                             PROJECT_ROL_ASSIGNMENT,
                             PROJECT_FLUJO_MANAGEMENT,
                             PROJECT_FLUJO_WATCH,
                             PROJECT_DEV_MANAGEMENT,
                             PROJECT_SPRINT_MANAGEMENT,
                             PROJECT_TUS_MANAGEMENET,
                             PROJECT_INFO_MANAGEMENT,
                             PROJECT_US_MANAGEMENT,
                             PROJECT_US_DEVELOP,
                             PROJECT_KANBAN_WATCH,
                             PROJECT_PB_WATCH,
                             PROJECT_SB_WATCH,
                         ])

DEF_ROLE_DEV_TEAM = ('dev_team','Development Team',
                     [
                         PROJECT_US_DEVELOP,
                         PROJECT_KANBAN_WATCH,
                         PROJECT_PB_WATCH,
                         PROJECT_SB_WATCH
                     ])

DEF_ROLE_PRODUCT_OWNER = ('product_owner','Product Owner',
                          [
                              PROJECT_KANBAN_WATCH,
                              PROJECT_PB_WATCH,
                              PROJECT_SB_WATCH,
                          ])


DEFAULT_ADMIN_ROLES = [
    DEF_ROLE_ADMIN
]

DEFAULT_PROJECT_ROLES = [
    DEF_ROLE_SCRUM_MASTER,
    DEF_ROLE_PRODUCT_OWNER,
    DEF_ROLE_DEV_TEAM
]