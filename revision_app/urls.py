from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter

from . import views

router = DefaultRouter()
router.register('mindmaps', views.MindmapViewSet)
router.register('categories', views.CategoryViewSet)
router.register('revisions', views.RevisionItemListViewSet, basename='revisions')

mindmap_router = NestedDefaultRouter(router, 'mindmaps', lookup='mindmap')
mindmap_router.register('revisions', views.RevisionItemViewSet, basename='mindmap-revisions')

urlpatterns = router.urls + mindmap_router.urls

