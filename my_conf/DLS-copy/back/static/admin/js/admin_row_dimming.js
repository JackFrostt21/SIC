// Затемнение невыбранных строк в админке Django
(function () {
    'use strict';

    function updateRowVisibility() {
        // Находим все таблицы с чекбоксами
        const tables = document.querySelectorAll('table, .table, .results table');

        tables.forEach(table => {
            const checkboxes = table.querySelectorAll('.action-select, input[name="_selected_action"]');
            const rows = table.querySelectorAll('tbody tr');

            if (checkboxes.length === 0 || rows.length === 0) return;

            // Считаем количество выбранных строк
            const checkedBoxes = table.querySelectorAll('.action-select:checked, input[name="_selected_action"]:checked');
            const hasSelection = checkedBoxes.length > 0;

            // Применяем классы к строкам
            rows.forEach(row => {
                const checkbox = row.querySelector('.action-select, input[name="_selected_action"]');

                if (checkbox && hasSelection) {
                    if (checkbox.checked) {
                        row.classList.remove('dimmed');
                        row.classList.add('selected');
                    } else {
                        row.classList.remove('selected');
                        row.classList.add('dimmed');
                    }
                } else {
                    // Если ничего не выбрано, убираем все классы
                    row.classList.remove('dimmed', 'selected');
                }
            });
        });
    }

    function initRowDimming() {
        // Обновляем при загрузке страницы
        updateRowVisibility();

        // Добавляем обработчики событий на все чекбоксы
        document.addEventListener('change', function (e) {
            if (e.target.matches('.action-select, input[name="_selected_action"], #action-toggle')) {
                // Небольшая задержка для корректной обработки
                setTimeout(updateRowVisibility, 10);
            }
        });

        // Обработчик для "Выбрать все"
        const selectAllCheckbox = document.querySelector('#action-toggle, .action-checkbox-column input');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', function () {
                setTimeout(updateRowVisibility, 50);
            });
        }

        // Обновляем при изменении DOM (для AJAX обновлений)
        const observer = new MutationObserver(function (mutations) {
            let shouldUpdate = false;
            mutations.forEach(function (mutation) {
                if (mutation.type === 'childList' &&
                    (mutation.target.tagName === 'TBODY' ||
                        mutation.target.classList.contains('results'))) {
                    shouldUpdate = true;
                }
            });
            if (shouldUpdate) {
                setTimeout(updateRowVisibility, 100);
            }
        });

        // Наблюдаем за изменениями в таблицах
        const containers = document.querySelectorAll('.results, .change-list, .content-wrapper');
        containers.forEach(container => {
            observer.observe(container, {
                childList: true,
                subtree: true
            });
        });
    }

    // Инициализируем когда DOM готов
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initRowDimming);
    } else {
        initRowDimming();
    }

    // Дополнительная инициализация для случаев когда скрипт загружается после DOM
    if (typeof jQuery !== 'undefined') {
        jQuery(document).ready(initRowDimming);
    }
})(); 