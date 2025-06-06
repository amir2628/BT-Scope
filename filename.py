# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class MonitoringDashboardProductionplanbt(models.Model):
    up_num = models.CharField(max_length=20, blank=True, null=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    order = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    limtz = models.CharField(max_length=50, blank=True, null=True)
    order_priority = models.CharField(max_length=100, blank=True, null=True)
    smz_chpu = models.CharField(max_length=50, blank=True, null=True)
    chpu_smz = models.CharField(max_length=50, blank=True, null=True)
    shipment = models.CharField(max_length=100, blank=True, null=True)
    operations = models.CharField(max_length=150, blank=True, null=True)
    time_for_piece = models.CharField(max_length=20, blank=True, null=True)
    time_for_batch = models.CharField(max_length=20, blank=True, null=True)
    planned_date_readiness = models.CharField(max_length=20, blank=True, null=True)
    ovk_manufacturing = models.CharField(max_length=50, blank=True, null=True)
    comments = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'monitoring_dashboard_productionplanbt'
