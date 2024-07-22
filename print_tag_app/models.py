from django.db import models

class RefTag(models.Model):
    ref_id = models.AutoField(primary_key=True)
    
    def __str__(self):
        return str(self.ref_id)  # Convert to string for a more descriptive representation

class Tag(models.Model):
    qr_code = models.CharField(max_length=255, null=False)
    po_no = models.CharField(max_length=100, null=True, blank=True)
    cust_sup = models.CharField(max_length=100, null=True, blank=True)
    part_name = models.CharField(max_length=255, null=True, blank=True)
    part_no = models.CharField(max_length=255, null=True, blank=True)
    lot_mat = models.CharField(max_length=100, null=True, blank=True)
    lot_prod = models.CharField(max_length=100, null=True, blank=True)
    model = models.CharField(max_length=100, null=True, blank=True)
    mc = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    qty = models.IntegerField(null=True, blank=True)
    ref_tag = models.ForeignKey(RefTag, on_delete=models.CASCADE)  # Foreign key field
