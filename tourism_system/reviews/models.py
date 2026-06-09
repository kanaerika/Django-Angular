from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel
from tour.models import Activity

class Review(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews', verbose_name="Voyageur")
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='reviews', verbose_name="Activité concernée")
    
    rating = models.PositiveIntegerField(
        choices=[(i, f"{i} étoile(s)") for i in range(1, 6)], 
        verbose_name="Note"
    )
    title = models.CharField(max_length=150, blank=True, verbose_name="Titre de l'avis")
    comment = models.TextField(verbose_name="Commentaire")
    is_visible = models.BooleanField(default=True, verbose_name="Avis visible", help_text="Décochez pour masquer l'avis (modération)")

    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        unique_together = ('user', 'activity')

    def __str__(self): return f"Avis de {self.user.username} sur {self.activity.title}"