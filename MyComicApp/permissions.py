from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Order, Product, Category, Role

@receiver(post_migrate)
def create_groups_and_permissions_on_startup(sender, **kwargs):
    create_groups_and_permissions()

def create_groups_and_permissions():
    User = get_user_model()

    # Crear grupos
    user_group, _ = Group.objects.get_or_create(name='User')
    vendedor_group, _ = Group.objects.get_or_create(name='Vendedor')
    admin_group, _ = Group.objects.get_or_create(name='Admin')

    # Asociar grupos a roles
    Role.objects.filter(name='User').update(group=user_group)
    Role.objects.filter(name='Vendedor').update(group=vendedor_group)
    Role.objects.filter(name='Admin').update(group=admin_group)

    # Obtener permisos para los modelos
    order_perms = Permission.objects.filter(content_type=ContentType.objects.get_for_model(Order))
    product_perms = Permission.objects.filter(content_type=ContentType.objects.get_for_model(Product))
    category_perms = Permission.objects.filter(content_type=ContentType.objects.get_for_model(Category))
    user_perms = Permission.objects.filter(content_type=ContentType.objects.get_for_model(User))

    # Asignar permisos al grupo 'Vendedor'
    vendedor_group.permissions.set(order_perms | product_perms | category_perms | user_perms)

    # Asignar permisos al grupo 'Admin'
    all_permissions = Permission.objects.all()
    admin_group.permissions.set(all_permissions)

    # Asociar permisos directamente a los usuarios basados en su rol
    for user in User.objects.all():
        if user.role and user.role.name == 'Vendedor':
            # Eliminar permisos para crear usuarios de tipo Admin y Vendedor
            user_perms_without_admin_vendedor = user_perms.exclude(codename__in=['add_user', 'change_user', 'delete_user'])
            user.user_permissions.set(order_perms | product_perms | category_perms | user_perms_without_admin_vendedor)
        elif user.role and user.role.name == 'Admin':
            user.user_permissions.set(all_permissions)

    # Asociar el superusuario al grupo 'Admin'
    superuser = User.objects.filter(is_superuser=True).first()
    if superuser:
        superuser.groups.add(admin_group)

    # Asociar usuarios a grupos basados en su rol
    for user in User.objects.all():
        if user.role and user.role.name == 'Vendedor':
            user.groups.add(vendedor_group)
        elif user.role and user.role.name == 'User':
            user.groups.add(user_group)
        elif user.role and user.role.name == 'Admin':
            user.groups.add(admin_group)