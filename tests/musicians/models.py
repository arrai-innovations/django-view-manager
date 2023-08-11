from django.db import models
from django.db.models.fields import related


class Bands(models.Model):
    name = models.CharField(max_length=1024)
    genre = models.CharField(max_length=1024)
    formed = models.DateField()

    class Meta:
        ordering = ("name",)
        default_related_name = "bands"

    def __str__(self):
        return f"{self.name} is a band."


class BandMembers(models.Model):
    band = related.ForeignKey("musicians.Bands", on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=1024)
    active_member = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)
        default_related_name = "band_members"

    def __str__(self):
        return f"{self.name} is in a band."


class BandInfo(models.Model):
    name = models.CharField(max_length=1024)
    genre = models.CharField(max_length=1024)

    class Meta:
        managed = False
        db_table = "band_info"
        ordering = ("name",)
        default_related_name = "musicians_bandinfo"

    def __str__(self):
        return f"{self.name} is info about a band."
