from django.contrib import admin
from django.db.models import Prefetch
from django.utils.html import format_html
from .models import Category, Mindmap, RevisionGroup, RevisionItem, RevisionLevel

admin.site.register(RevisionLevel)

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):    
    list_display = ['title', 'mindmaps_count']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('mindmaps')

    def mindmaps_count(self, model):
        return model.mindmaps.count()

@admin.register(Mindmap)
class MindmapAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'creation_date', 'image', 'revision_count', 'revision_level']

    def get_queryset(self, request):
        return super().get_queryset(request)\
            .select_related('category', 'revisions')\
            .prefetch_related('revisions__revision_item')\
            .prefetch_related('revisions__revision_level')

    def image(self, model):
        image_link = str(model.image_link)
        return format_html('<a href="{}">{}</a>', image_link, image_link[:10]+"..."+image_link[-10:])

    def revision_count(self, model):
        return model.revisions.revision_item.count()

    def revision_level(self, model):
        return str(model.revisions.revision_level)

@admin.register(RevisionGroup)
class RevisionGroupAdmin(admin.ModelAdmin):
    list_select_related = ['mindmap__category']
    list_display = ['mindmap_title', 'revision_level', 'revision_count']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('revision_item')

    @admin.display(ordering='mindmap')
    def mindmap_title(self, model):
        return str(model)

    def revision_count(self, model):
        return model.revision_item.count()



@admin.register(RevisionItem)
class RevisionItemAdmin(admin.ModelAdmin):
    list_select_related = ['revision_group__mindmap__category']
    list_display = ['date', 'category', 'mindmap', 'revision_done']

    def category(self, model):
        return model.revision_group.mindmap.category
    
    def mindmap(self, model):
        return model.revision_group.mindmap
