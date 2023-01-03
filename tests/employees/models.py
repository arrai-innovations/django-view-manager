from django.db import models


class Employee(models.Model):
    first_name = models.CharField(max_length=1024)
    last_name = models.CharField(max_length=1024)

    class Meta:
        ordering = ("last_name", "first_name")
        default_related_name = "employees"

    def __str__(self):
        return f"{self.employee} likes {self.name}."


class EmployeeLikes(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=1024)

    class Meta:
        managed = False
        db_table = "employees_employeelikes"
        ordering = ("name",)
        default_related_name = "likes"

    def __str__(self):
        return f"{self.employee} likes {self.name}."
