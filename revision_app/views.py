from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from .models import Category, Mindmap, RevisionGroup, RevisionItem
from .serializers import CategorySerializer, FormMindmapSerializer, ListMindmapSerializer, RevisionItemSerializer

# Create your views here.
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    

class MindmapViewSet(ModelViewSet):
    queryset = Mindmap.objects.prefetch_related('revisions')\
                .select_related('category')\
                .prefetch_related('revisions__revision_item', 'revisions__revision_level')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ListMindmapSerializer
        return FormMindmapSerializer


class RevisionItemViewSet(ModelViewSet):

    serializer_class = RevisionItemSerializer
    
    def get_queryset(self):
        revision_group = RevisionGroup.objects.get(mindmap__id=self.kwargs['mindmap_pk'])
        return RevisionItem.objects.filter(revision_group__id=revision_group.id)

    def get_serializer_context(self):
        return {'mindmap_pk': self.kwargs['mindmap_pk']}