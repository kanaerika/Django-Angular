# create_roles.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tourism_system.settings')
django.setup()

from account.models import Role

def create_roles():
    roles = [
        {'name': 'Admin', 'description': 'Administrateur'},
        {'name': 'Guide', 'description': 'Guide touristique'},
        {'name': 'Tourist', 'description': 'Touriste'},
    ]
    
    for role_data in roles:
        role, created = Role.objects.get_or_create(
            name=role_data['name'],
            defaults={'description': role_data['description']}
        )
        if created:
            print(f"✅ Rôle '{role.name}' créé avec succès")
        else:
            print(f"⚠️ Rôle '{role.name}' existe déjà")
    
    print("\n✨ Tous les rôles sont configurés !")

if __name__ == '__main__':
    create_roles()