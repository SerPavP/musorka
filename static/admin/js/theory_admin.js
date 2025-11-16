// JavaScript для улучшения админ-панели теории

(function($) {
    $(document).ready(function() {
        // Автоматическое изменение уровня при выборе родителя
        var $parentField = $('#id_parent');
        var $levelField = $('#id_level');
        
        if ($parentField.length && $levelField.length) {
            $parentField.on('change', function() {
                if ($(this).val()) {
                    // Если выбран родитель, устанавливаем уровень 2
                    $levelField.val(2);
                    // Показываем подсказку
                    if (!$('#parent-help').length) {
                        $parentField.after('<p id="parent-help" style="color: #27ae60; font-size: 12px; margin-top: 5px;">✓ Уровень автоматически установлен на 2</p>');
                    }
                } else {
                    // Если родитель не выбран, можно выбрать уровень вручную
                    $('#parent-help').remove();
                }
            });
        }
        
        // Автогенерация section_id из title
        var $titleField = $('#id_title');
        var $sectionIdField = $('#id_section_id');
        
        if ($titleField.length && $sectionIdField.length && !$sectionIdField.val()) {
            $titleField.on('blur', function() {
                if (!$sectionIdField.val()) {
                    var title = $(this).val();
                    // Преобразуем в section_id: убираем спецсимволы, заменяем пробелы на дефисы
                    var sectionId = title
                        .toLowerCase()
                        .replace(/[^\w\s-]/g, '')
                        .replace(/\s+/g, '-')
                        .replace(/-+/g, '-')
                        .replace(/^-|-$/g, '');
                    $sectionIdField.val(sectionId);
                }
            });
        }
        
        // Подсветка активных/неактивных секций в списке
        $('.field-is_active_badge').each(function() {
            var $row = $(this).closest('tr');
            if ($(this).text().includes('Неактивна')) {
                $row.css('opacity', '0.6');
            }
        });
        
        // Улучшенное отображение контента в списке (показываем первые 100 символов)
        $('.field-content').each(function() {
            var content = $(this).text();
            if (content.length > 100) {
                $(this).text(content.substring(0, 100) + '...');
                $(this).attr('title', content);
            }
        });
        
        // Добавляем кнопку "Предпросмотр" для контента
        if ($('#id_content').length) {
            var $contentField = $('#id_content');
            var $previewBtn = $('<button type="button" id="preview-btn" style="margin-top: 10px; padding: 8px 15px; background: #27ae60; color: white; border: none; border-radius: 4px; cursor: pointer;">👁 Предпросмотр</button>');
            $contentField.after($previewBtn);
            
            $previewBtn.on('click', function() {
                var content = $contentField.val();
                var $modal = $('<div id="preview-modal" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 10000; overflow: auto;">' +
                    '<div style="background: white; margin: 50px auto; padding: 30px; max-width: 900px; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">' +
                    '<h2 style="margin-top: 0; color: #27ae60;">Предпросмотр содержимого</h2>' +
                    '<div style="border: 1px solid #ddd; padding: 20px; border-radius: 4px; max-height: 600px; overflow: auto; background: #f9f9f9;">' +
                    content +
                    '</div>' +
                    '<button type="button" id="close-preview" style="margin-top: 20px; padding: 10px 20px; background: #27ae60; color: white; border: none; border-radius: 4px; cursor: pointer;">Закрыть</button>' +
                    '</div></div>');
                $('body').append($modal);
                
                $('#close-preview, #preview-modal').on('click', function(e) {
                    if (e.target === this) {
                        $('#preview-modal').remove();
                    }
                });
            });
        }
        
        // Подсветка измененных полей
        $('input, textarea, select').on('change', function() {
            $(this).css('background-color', '#fff9e6');
        });
    });
})(django.jQuery);

