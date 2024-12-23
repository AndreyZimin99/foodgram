from django.contrib import admin

from .models import Ingredient, Recipe, Tag


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'text',
                    'cooking_time')
    # list_filter = ('name', 'author', 'text',
    #                'ingredients', 'tags', 'cooking_time')
    list_filter = ('name', 'author', 'text',
                   'ingredients', 'cooking_time')
    search_fields = ('text', 'author__username', 'title')
    ordering = ('-name',)
    raw_id_fields = ('author',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    list_filter = ('name', 'slug')
    search_fields = ('name', 'slug')
    ordering = ('id',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('id',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
