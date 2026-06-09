from rest_framework import serializers

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    Un ModelSerializer qui permet de spécifier dynamiquement les champs à inclure/exclure
    Utilisation: ?fields=id,name,email ou ?exclude=password
    """
    
    def __init__(self, *args, **kwargs):
        # Récupérer les champs dynamiques des kwargs
        fields = kwargs.pop('fields', None)
        exclude = kwargs.pop('exclude', None)
        
        super().__init__(*args, **kwargs)
        
        if fields is not None:
            # Ne garder que les champs spécifiés
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        
        if exclude is not None:
            # Exclure les champs spécifiés
            not_allowed = set(exclude)
            for field_name in not_allowed:
                if field_name in self.fields:
                    self.fields.pop(field_name)