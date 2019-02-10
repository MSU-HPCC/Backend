from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.
class ScriptGenInfo(models.Model):
    Wall_time = models.CharField( max_length=100)
    job_name = models.CharField( max_length=100)
    script_path = models.CharField( max_length=100)

    nodes = models.IntegerField( validators=[MinValueValidator(0)])
    memory = models.CharField( max_length=100)
    CPUs = models.IntegerField(validators=[MinValueValidator(0)])
    MemoryPerCPU = models.CharField( max_length=100)

    def __str__(self):
        string = str(self.Wall_time)+ str(self.job_name)+str(self.script_path)+str(self.nodes)+str(self.memory)+str(self.CPUs)+str(self.MemoryPerCPU)
        return string