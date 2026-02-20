# example Document model with TextField for extracted content and FileField for docx upload
from django.db import models

class Document(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)  # extracted text from docx
    
    def __str__(self):
        return self.title