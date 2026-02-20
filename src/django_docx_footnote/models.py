from django.db import models

class DocumentWithFootnotes(models.Model):
    id = models.CharField(max_length=200)
    content = models.TextField()
    footnotes = models.JSONField()
    
    class Meta:
        # CRITICAL: No DB table created
        managed = False
