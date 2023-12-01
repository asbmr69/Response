from django.db import models

# Create your models here.
class Query(models.Model):
    query_text = models.CharField(max_length=255)

class SearchResult(models.Model):
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    link = models.URLField()
    snippet = models.TextField()

    def __str__(self):
        return f"{self.query.query_text}-{self.title}"