from django.utils.text import slugify
import uuid
import random
import string

def generate_unique_slug(model_instance, slugable_field_name, slug_field_name='slug'):
    """
    Générer un slug unique pour un modèle
    """
    slug = slugify(getattr(model_instance, slugable_field_name))
    unique_slug = slug
    extension = 1
    
    ModelClass = model_instance.__class__
    
    while ModelClass.objects.filter(**{slug_field_name: unique_slug}).exists():
        unique_slug = f'{slug}-{extension}'
        extension += 1
    
    return unique_slug


def generate_reference_number(prefix='REF'):
    """
    Générer un numéro de référence unique
    """
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"{prefix}-{random_part}"


def format_price(price):
    """
    Formater un prix avec séparateur de milliers
    """
    return f"{price:,.2f}".replace(",", " ")


def calculate_duration(start_date, end_date):
    """
    Calculer la durée entre deux dates en jours
    """
    delta = end_date - start_date
    return delta.days


def get_client_ip(request):
    """
    Récupérer l'adresse IP du client
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def validate_file_extension(value, allowed_extensions=['jpg', 'jpeg', 'png', 'gif']):
    """
    Valider l'extension d'un fichier
    """
    import os
    ext = os.path.splitext(value.name)[1].lower().replace('.', '')
    if ext not in allowed_extensions:
        raise ValidationError(f"Extension non supportée. Utilisez: {', '.join(allowed_extensions)}")