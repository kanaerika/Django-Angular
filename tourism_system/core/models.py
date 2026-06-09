from django.db import models

class TimeStampedModel(models.Model):
    """
    Modèle abstrait qui ajoute les champs created_at et updated_at
    Tous les modèles qui en héritent auront automatiquement ces champs
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de modification")

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteModel(models.Model):
    """
    Modèle abstrait pour la suppression douce (soft delete)
    Les enregistrements ne sont pas vraiment supprimés mais marqués comme supprimés
    """
    is_deleted = models.BooleanField(default=False, verbose_name="Supprimé")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de suppression")

    class Meta:
        abstract = True

    def soft_delete(self):
        """Marquer l'enregistrement comme supprimé"""
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restaurer un enregistrement supprimé"""
        self.is_deleted = False
        self.deleted_at = None
        self.save()