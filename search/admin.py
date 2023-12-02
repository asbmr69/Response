from django.contrib import admin

# Register your models here.
from .models import Query, SearchResult

admin.site.register(Query)
admin.site.register(SearchResult)
