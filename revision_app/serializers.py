from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from .models import Category, Mindmap, RevisionGroup, RevisionItem, RevisionLevel

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']

class ListMindmapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mindmap
        fields = ['id', 'title', 'description', 'category', 'image_link',
            'creation_date', 'revision_count', 'revision_level', 'next_revision_date']

    revision_level = serializers.SerializerMethodField(method_name='get_revision_level')
    revision_count = serializers.SerializerMethodField(method_name='get_revision_count')
    next_revision_date = serializers.SerializerMethodField(method_name='get_next_revision_date')

    def get_revision_level(self, model):
        try:
            return model.revisions.revision_level.level
        except ObjectDoesNotExist:
                return None

    def get_revision_count(self, model):
        try:
            return model.revisions.revision_item.count()
        except ObjectDoesNotExist:
            return 0

    def get_next_revision_date(self, model):
        try:
            data = model.revisions.revision_item.first()
            if data is not None:
                return data.date
            return None
        except ObjectDoesNotExist:
            return None

class FormMindmapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mindmap
        fields = ['id', 'title', 'description', 'category', 'image_link',
            'creation_date', 'revision_level']

    revision_level = serializers.PrimaryKeyRelatedField(write_only=True, queryset=RevisionLevel.objects.all())
    creation_date = serializers.DateTimeField(required=False)

    def create_revisions_routine(self, rev_group):
        rev_items = []
        # Every day for first week
        for x in range(7):
            rev_items.append(RevisionItem(revision_group=rev_group, date=datetime.now() + timedelta(days=x)))
        # Every other day for second week
        for x in range(3):
            rev_items.append(RevisionItem(revision_group=rev_group, date=datetime.now() + timedelta(days=9+2*x)))
        # Twice a week for 3-4th week
        for x in [18,21,25,28]:
            rev_items.append(RevisionItem(revision_group=rev_group, date=datetime.now() + timedelta(days=x)))
        # Once a week for 2nd-3rd month
        for x in [35,42,49,56,63,70,77,84,91]:
            rev_items.append(RevisionItem(revision_group=rev_group, date=datetime.now() + timedelta(days=x)))
        # Once a month after 3rd month
        # To do, Currently added manually
        RevisionItem.objects.bulk_create(rev_items)

    def create(self, validated_data):
        level = validated_data['revision_level']
        del validated_data['revision_level']
        mindmap = Mindmap(**validated_data)
        mindmap.creation_date = datetime.now()
        mindmap.save()
        rev_group = RevisionGroup.objects.create(mindmap=mindmap, revision_level=level)
        self.create_revisions_routine(rev_group)
        return mindmap

    def update(self, instance, validated_data):
        level = validated_data['revision_level']
        del validated_data['revision_level']
        RevisionGroup.objects.filter(mindmap=instance).update(revision_level=level)
        return super().update(instance, validated_data)


# For sub endpoint of mindmap
class RevisionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevisionItem
        fields = ['id','date', 'revision_done']
    
    def create(self, validated_data):
        mindmap_id = self.context['mindmap_pk']
        revision_group = RevisionGroup.objects.get(mindmap__id=mindmap_id)
        return RevisionItem.objects.create(revision_group=revision_group, **validated_data)

    
# For revisions own root endpoint
class RevisionItemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevisionItem
        fields = ['id', 'date', 'revision_done',
            'mindmap_title',  'mindmap_created', 'mindmap_category']

    mindmap_title = serializers.SerializerMethodField(method_name='get_mindmap_title')
    mindmap_created = serializers.SerializerMethodField(method_name='get_mindmap_created')
    mindmap_category = serializers.SerializerMethodField(method_name='get_mindmap_category')

    def get_mindmap_title(self, model):
        return model.revision_group.mindmap.title
    
    def get_mindmap_created(self, model):
        return model.revision_group.mindmap.creation_date
    
    def get_mindmap_category(self, model):
        return model.revision_group.mindmap.category.title


class RevisionLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevisionLevel
        fields = ['id', 'level']
