from wsgiref import validate
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from .models import Mindmap, RevisionGroup, RevisionItem, RevisionLevel

class RevisionGroupSerializer(serializers.RelatedField):
    def to_representation(self, value):
        return value.revision_level.level


class ListMindmapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mindmap
        fields = ['id', 'title', 'description', 'category', 'image_link',
            'creation_date', 'revision_count', 'revision_level']

    revision_level = serializers.SerializerMethodField(method_name='get_revision_level')
    revision_count = serializers.SerializerMethodField(method_name='get_revision_count')

    def get_revision_level(self, model):
        return model.revisions.revision_level.level

    def get_revision_count(self, model):
        try:
            return model.revisions.revision_item.count()
        except ObjectDoesNotExist:
            return 0

class FormMindmapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mindmap
        fields = ['id', 'title', 'description', 'category', 'image_link',
            'creation_date', 'revision_level']

    revision_level = serializers.PrimaryKeyRelatedField(write_only=True, queryset=RevisionLevel.objects.all())

    def create(self, validated_data):
        level = validated_data['revision_level']
        del validated_data['revision_level']
        mindmap = Mindmap(**validated_data)
        mindmap.save()
        RevisionGroup.objects.create(mindmap=mindmap, revision_level=level)
        return mindmap

    def update(self, instance, validated_data):
        level = validated_data['revision_level']
        del validated_data['revision_level']
        RevisionGroup.objects.filter(mindmap=instance).update(revision_level=level)
        return super().update(instance, validated_data)


class RevisionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevisionItem
        fields = ['id','date', 'revision_done']
    
    def create(self, validated_data):
        mindmap_id = self.context['mindmap_pk']
        revision_group = RevisionGroup.objects.get(mindmap__id=mindmap_id)
        return RevisionItem.objects.create(revision_group=revision_group, **validated_data)

    