import secrets

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from unidecode import unidecode

User = get_user_model()


def generate_short_code():
    # Генерирует URL-безопасную строку.
    # token_urlsafe(4) выдает ~6 символов (например, 'Xy7_2Q')
    return secrets.token_urlsafe(4)


class Ingredient(models.Model):
    name = models.CharField(_('name'), max_length=128, unique=True)
    measurement_unit = models.CharField(_('measurement unit'), max_length=64)

    class Meta:
        verbose_name = _('Ingredient')
        verbose_name_plural = _('Ingredients')
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    name = models.CharField(_('name'), max_length=50, unique=True)
    slug = models.SlugField(_('slug'), max_length=50, unique=True)

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name=_('author'),
        on_delete=models.CASCADE
    )
    name = models.CharField(_('name'), max_length=50)
    image = models.ImageField(
        _('image'),
        upload_to='recipes/'
    )
    text = models.TextField(_('description'))
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name=_('ingredient'),
        through='RecipeIngredient',
        related_name='recipes'
    )
    tags = models.ManyToManyField(Tag, related_name='recipes')
    cooking_time = models.PositiveIntegerField(_('cooking time'), default=5)

    class Meta:
        verbose_name = _('Recipe')
        verbose_name_plural = _('Recipes')
        ordering = ('name',)

    def __str__(self):
        return self.name

    @property
    def short_url(self):
        return f'https://yourdomain.com{self.short_link.code}'


class ShortLink(models.Model):
    code = models.CharField(
        max_length=10,
        unique=True,
        default=generate_short_code,
        editable=False
    )
    recipe = models.OneToOneField(
        Recipe,
        on_delete=models.CASCADE,
        related_name='short_link'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.code} -> {self.recipe.title}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name=_('recipe'),
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name=_('ingredient'),
        on_delete=models.CASCADE
    )
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _('RecipeIngredient')
        verbose_name_plural = _('RecipeIngredients')

    def __str__(self):
        return f'{self.ingredient.title} {self.amount}'


class Favorite(models.Model):
    user  = models.ForeignKey(
        User,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name=_('recipe'),
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(_('created_at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Favorite')
        unique_together = ('user', 'recipe',)

    def __str__(self):
        return f'Рецепт: {self.recipe.title} добавлен в избранное'


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name=_('subscriber')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name=_('author')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Subscription')
        verbose_name_plural = _('Subscriptions')
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            ),
            models.CheckConstraint(
                condition=models.Q(user=models.F('author')),
                name='prevent_self_subscription'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name=_('recipe'),
        on_delete=models.CASCADE,
        related_name='in_carts',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Cart item')
        verbose_name_plural = _('Cart items')
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart_item'
            ),
        ]

    def __str__(self):
        return f'{self.recipe} в корзине у {self.user}'
