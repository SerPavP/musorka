from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils.html import escape
from django.forms import Textarea
from django.db import models
from .models import TheorySection, TheoryNavigation


class TheorySectionInline(admin.TabularInline):
    """Inline для редактирования подглав внутри глав"""
    model = TheorySection
    fk_name = 'parent'
    extra = 1
    fields = ('section_id', 'title', 'order', 'is_active')
    verbose_name = 'Подглава'
    verbose_name_plural = 'Подглавы'
    classes = ('collapse',)
    ordering = ('order',)
    show_change_link = True
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('parent')


@admin.register(TheorySection)
class TheorySectionAdmin(admin.ModelAdmin):
    list_display = ['display_title', 'section_id', 'level_badge', 'order', 'is_active', 'is_active_badge', 'children_count', 'parent_link', 'updated_at']
    list_filter = ['level', 'is_active', 'created_at', 'parent']
    search_fields = ['title', 'section_id', 'content']
    list_editable = ['order', 'is_active']
    ordering = ['order', 'level', 'id']
    list_per_page = 50
    inlines = [TheorySectionInline]
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 20, 'cols': 100})},
    }
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('section_id', 'title', 'parent', 'level', 'order', 'is_active'),
            'description': mark_safe('<strong>Уровень 1</strong> - основные главы (Введение, Актуальность, разделы 1, 2, 3...)<br>'
                                   '<strong>Уровень 2</strong> - подглавы (Определение отходов, Классификация отходов и т.д.)<br>'
                                   'При выборе родительской секции уровень автоматически устанавливается на 2.')
        }),
        ('Содержимое', {
            'fields': ('content',),
            'classes': ('wide',),
            'description': mark_safe('HTML содержимое секции. Можно использовать HTML теги для форматирования.<br>'
                                   '<strong>Доступные теги:</strong> &lt;p&gt;, &lt;h1&gt;-&lt;h6&gt;, &lt;ul&gt;, &lt;ol&gt;, &lt;li&gt;, '
                                   '&lt;strong&gt;, &lt;em&gt;, &lt;table&gt;, &lt;img&gt; и другие.')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')
    
    def display_title(self, obj):
        """Отображает заголовок с отступом в зависимости от уровня"""
        indent = '&nbsp;&nbsp;&nbsp;&nbsp;' * (obj.level - 1)
        if obj.level == 1:
            icon = '📖'
        else:
            icon = '📄'
        return mark_safe(f'{indent}{icon} {escape(obj.title)}')
    display_title.short_description = 'Заголовок'
    display_title.admin_order_field = 'title'
    
    def level_badge(self, obj):
        """Бейдж уровня с цветом"""
        if obj.level == 1:
            color = '#27ae60'
            text = 'Глава'
        else:
            color = '#3498db'
            text = 'Подглава'
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">{}</span>',
            color, text
        )
    level_badge.short_description = 'Уровень'
    level_badge.admin_order_field = 'level'
    
    def is_active_badge(self, obj):
        """Бейдж активности"""
        if obj.is_active:
            return format_html(
                '<span style="background: #27ae60; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px;">✓ Активна</span>'
            )
        else:
            return format_html(
                '<span style="background: #e74c3c; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px;">✗ Неактивна</span>'
            )
    is_active_badge.short_description = 'Статус'
    is_active_badge.admin_order_field = 'is_active'
    
    def children_count(self, obj):
        """Количество подглав"""
        count = obj.children.count()
        if count > 0:
            url = reverse('admin:classifier_theorysection_changelist') + f'?parent__id__exact={obj.id}'
            return format_html('<a href="{}">{} подглав(ы)</a>', url, count)
        return '-'
    children_count.short_description = 'Подглавы'
    
    def parent_link(self, obj):
        """Ссылка на родительскую секцию"""
        if obj.parent:
            url = reverse('admin:classifier_theorysection_change', args=[obj.parent.pk])
            return format_html('<a href="{}" style="color: #27ae60; font-weight: bold;">{}</a>', url, obj.parent.title)
        return format_html('<span style="color: #999;">—</span>')
    parent_link.short_description = 'Родитель'
    parent_link.admin_order_field = 'parent'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Ограничиваем выбор родителя только секциями более низкого уровня
        if obj:
            form.base_fields['parent'].queryset = TheorySection.objects.filter(
                level__lt=obj.level
            ).exclude(id=obj.id)
        else:
            # Для новых объектов показываем все секции уровня 1
            form.base_fields['parent'].queryset = TheorySection.objects.filter(level=1)
        
        # Добавляем JavaScript для автоматического изменения уровня при выборе родителя
        if 'parent' in form.base_fields:
            form.base_fields['parent'].help_text = 'При выборе родительской секции уровень автоматически установится на 2'
        
        return form
    
    class Media:
        css = {
            'all': ('admin/css/theory_admin.css',)
        }
        js = ('admin/js/theory_admin.js',)
    
    def save_model(self, request, obj, form, change):
        """Автоматически устанавливаем уровень при выборе родителя"""
        if obj.parent:
            obj.level = obj.parent.level + 1
        elif not obj.level:
            obj.level = 1
        super().save_model(request, obj, form, change)
    
    actions = ['make_active', 'make_inactive', 'set_level_1', 'set_level_2', 'duplicate_sections']
    
    def make_active(self, request, queryset):
        """Активировать выбранные секции"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'✓ {updated} секций активировано.', level='success')
    make_active.short_description = '✅ Активировать выбранные секции'
    
    def make_inactive(self, request, queryset):
        """Деактивировать выбранные секции"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'✗ {updated} секций деактивировано.', level='warning')
    make_inactive.short_description = '❌ Деактивировать выбранные секции'
    
    def set_level_1(self, request, queryset):
        """Установить уровень 1"""
        updated = queryset.update(level=1, parent=None)
        self.message_user(request, f'✓ {updated} секций установлено на уровень 1 (основные главы).', level='success')
    set_level_1.short_description = '📖 Установить уровень 1 (основные главы)'
    
    def set_level_2(self, request, queryset):
        """Установить уровень 2"""
        updated = queryset.update(level=2)
        self.message_user(request, f'✓ {updated} секций установлено на уровень 2 (подглавы).', level='success')
    set_level_2.short_description = '📄 Установить уровень 2 (подглавы)'
    
    def duplicate_sections(self, request, queryset):
        """Дублировать выбранные секции"""
        count = 0
        for obj in queryset:
            obj.pk = None
            obj.section_id = f"{obj.section_id}_copy_{count}"
            obj.title = f"{obj.title} (копия)"
            obj.order = obj.order + 1000  # Ставим в конец
            obj.save()
            count += 1
        self.message_user(request, f'✓ {count} секций продублировано.', level='success')
    duplicate_sections.short_description = '📋 Дублировать выбранные секции'


@admin.register(TheoryNavigation)
class TheoryNavigationAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_editable = ['is_active']
    list_filter = ['is_active']
    search_fields = ['name']


# Добавляем кастомный заголовок для админ-панели
admin.site.site_header = "Управление теорией машинного обучения"
admin.site.site_title = "Админ-панель теории"
admin.site.index_title = "Управление контентом"
