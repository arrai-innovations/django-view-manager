from django.db import models


class Pets(models.Model):
    name = models.CharField(max_length=1024)

    class Meta:
        managed = False
        db_table = "animals_pets"
        ordering = ("name",)
        default_related_name = "pets"

    def __str__(self):
        return f"{self.name} is a pet."
