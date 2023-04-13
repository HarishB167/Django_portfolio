from django.db.models import Prefetch
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from .models import Category, Mindmap, RevisionGroup, RevisionItem, RevisionLevel
from .serializers import CategorySerializer, FormMindmapSerializer\
            , ListMindmapSerializer, RevisionItemListSerializer\
            , RevisionItemSerializer, RevisionLevelSerializer

# Create your views here.
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    

class MindmapViewSet(ModelViewSet):
    queryset = Mindmap.objects.prefetch_related('revisions')\
                .select_related('category')\
                .prefetch_related(
                    Prefetch('revisions__revision_item', 
                        queryset=RevisionItem.objects.order_by('date').filter(revision_done=False)),
                    'revisions__revision_level')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ListMindmapSerializer
        return FormMindmapSerializer


# For sub endpoint of mindmap for managing revision items
class RevisionItemViewSet(ModelViewSet):

    serializer_class = RevisionItemSerializer
    
    def get_queryset(self):
        revision_group = RevisionGroup.objects.get(mindmap__id=self.kwargs['mindmap_pk'])
        return RevisionItem.objects.filter(revision_group__id=revision_group.id)

    def get_serializer_context(self):
        return {'mindmap_pk': self.kwargs['mindmap_pk']}


# For listing revision items in home page
class RevisionItemListViewSet(ModelViewSet):
    serializer_class = RevisionItemListSerializer

    def get_queryset(self):
        revision_items = RevisionItem.objects.select_related('revision_group__mindmap__category')\
                .order_by('date', 'revision_group__mindmap__category', 
                'revision_group__mindmap__creation_date')
        return revision_items

    def list(self, request, *args, **kwargs):
        queryset = list(self.get_queryset())
        date_list = [revitem.date for revitem in queryset]
        date_list = list(dict.fromkeys(date_list))

        def filter_for_date(item_list, date):
            return [item for item in item_list if item.date == date]

        result = []
        for date in date_list:
            data = {"date": date}
            revision_items = filter_for_date(queryset, date)
            data["revisions"] = self.serializer_class(revision_items, many=True).data
            result.append(data)

        return Response(result)


class RevisionLevelViewSet(ModelViewSet):
    serializer_class = RevisionLevelSerializer
    queryset = RevisionLevel.objects.all()