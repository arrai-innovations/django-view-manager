from django.db import models


class Sweets(models.Model):
    name = models.CharField(max_length=1024)

    class Meta:
        managed = False
        db_table = "food_sweets"
        ordering = ("name",)
        default_related_name = "sweets"

    def __str__(self):
        return f"{self.name} is sweet."
