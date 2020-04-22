from django.db import models

# Create your models here.


class StockMonitor(models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=30)
    raise_ratio = models.FloatField(default=0.05)
    drop_ratio = models.FloatField(default=0.05)
    hold = models.BooleanField(default=True)

    def __str__(self):
        return '{}({})'.format(self.name, self.code)


class Holiday(models.Model):
    date = models.CharField(max_length=20, primary_key=True)
    reason = models.CharField(max_length=50)


class SmsLog(models.Model):
    day = models.CharField(max_length=20)
    time = models.CharField(max_length=10)
    code = models.CharField(max_length=10)

    class Meta:
        index_together = [('code', 'day')]

