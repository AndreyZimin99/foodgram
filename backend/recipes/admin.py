from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    ShortLink,
    Tag,
)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'favorite_count')
    list_filter = ('tags',)
    search_fields = ('author__username', 'name')
    ordering = ('-name',)

    def favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    favorite_count.short_description = 'Число добавлений в избранное'


class IngredientAdmin(admin.ModelAdmin):
    search_fields = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(Favorite)
admin.site.register(RecipeIngredient)
admin.site.register(ShoppingCart)
admin.site.register(ShortLink)
