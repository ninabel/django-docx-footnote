# library document list and detail views
from django.shortcuts import render, get_object_or_404
from .models import Document

def document_list(request):
    documents = Document.objects.all()
    return render(request, 'document_list.html', {'documents': documents})

def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    return render(request, 'document.html', {'document': document})