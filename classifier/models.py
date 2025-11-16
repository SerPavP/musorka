from django.db import models
from django.core.cache import cache
from django.utils.text import slugify


class TheorySection(models.Model):
    """Модель для секций теории"""
    section_id = models.CharField(max_length=100, unique=True, verbose_name="ID секции")
    title = models.CharField(max_length=500, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержимое (HTML)")
    level = models.IntegerField(default=1, verbose_name="Уровень вложенности")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="Родительская секция"
    )
    order = models.IntegerField(default=0, verbose_name="Порядок отображения")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Секция теории"
        verbose_name_plural = "Секции теории"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.title} (уровень {self.level})"

    def save(self, *args, **kwargs):
        """При сохранении очищаем кэш"""
        super().save(*args, **kwargs)
        cache.delete('theory_navigation')
        cache.delete('theory_sections')

    def delete(self, *args, **kwargs):
        """При удалении очищаем кэш"""
        super().delete(*args, **kwargs)
        cache.delete('theory_navigation')
        cache.delete('theory_sections')


class TheoryNavigation(models.Model):
    """Модель для навигации (можно использовать для дополнительных настроек)"""
    name = models.CharField(max_length=200, verbose_name="Название")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Навигация теории"
        verbose_name_plural = "Навигация теории"

    def __str__(self):
        return self.name
