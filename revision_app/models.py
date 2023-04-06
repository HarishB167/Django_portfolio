from django.db import models

# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.title


class Mindmap(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='mindmaps')
    image_link = models.URLField()
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.title} : {self.category.title}'


class RevisionLevel(models.Model):
    level = models.CharField(max_length=10)

    def __str__(self) -> str:
        return self.level


class RevisionGroup(models.Model):
    REVISION_LEVELS = [
        ('L1', 'Level 1'),
        ('L2', 'Level 2'),
        ('L3', 'Level 3'),
        ('L4', 'Level 4'),
        ('L5', 'Level 5'),
    ]
    mindmap = models.OneToOneField(Mindmap, on_delete=models.CASCADE, related_name='revisions')
    revision_level = models.ForeignKey(RevisionLevel, on_delete=models.PROTECT, related_name='revisions')

    def __str__(self) -> str:
        return f'{self.mindmap.title} : ({self.mindmap.category})'

    class Meta:
        ordering = ['mindmap__category__title', 'mindmap__title']


class RevisionItem(models.Model):
    revision_group = models.ForeignKey(RevisionGroup, on_delete=models.CASCADE, related_name='revision_item')
    date = models.DateField()
    revision_done = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.date}'

    def __repr__(self) -> str:
        return f'{self.date} : {self.revision_group.mindmap.title} : {self.revision_group.mindmap.category}'
