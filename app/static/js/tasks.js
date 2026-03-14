// Фильтрация по возрасту и категориям
document.addEventListener('DOMContentLoaded', function() {
    const age14Btn = document.getElementById('age-14');
    const age18Btn = document.getElementById('age-18');
    const categoryCheckboxes = document.querySelectorAll('.category-filter');
    const taskCards = document.querySelectorAll('.task-card');

    function filterTasks() {
        const selectedAge = age14Btn.classList.contains('bg-yellow-500') ? 14 : 18;
        const selectedCategories = Array.from(categoryCheckboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.value);

        taskCards.forEach(card => {
            const taskAge = parseInt(card.dataset.age) || 0;
            const taskType = card.dataset.type;

            let ageOk = (selectedAge === 14 && taskAge <= 14) || (selectedAge === 18); // 18+ видит все
            let categoryOk = selectedCategories.length === 0 || selectedCategories.includes(taskType);

            if (ageOk && categoryOk) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }

    age14Btn.addEventListener('click', function() {
        age14Btn.classList.add('bg-yellow-500', 'text-white');
        age14Btn.classList.remove('bg-gray-200', 'dark:bg-gray-700', 'text-gray-800', 'dark:text-white');
        age18Btn.classList.remove('bg-yellow-500', 'text-white');
        age18Btn.classList.add('bg-gray-200', 'dark:bg-gray-700', 'text-gray-800', 'dark:text-white');
        filterTasks();
    });

    age18Btn.addEventListener('click', function() {
        age18Btn.classList.add('bg-yellow-500', 'text-white');
        age18Btn.classList.remove('bg-gray-200', 'dark:bg-gray-700', 'text-gray-800', 'dark:text-white');
        age14Btn.classList.remove('bg-yellow-500', 'text-white');
        age14Btn.classList.add('bg-gray-200', 'dark:bg-gray-700', 'text-gray-800', 'dark:text-white');
        filterTasks();
    });

    categoryCheckboxes.forEach(cb => cb.addEventListener('change', filterTasks));

    // Модальное окно
    window.openTaskModal = function(taskId) {
        fetch(`/tasks/${taskId}`)
            .then(res => res.json())
            .then(task => {
                window.dispatchEvent(new CustomEvent('open-task-modal', { detail: task }));
            });
    };

    window.acceptTask = function(taskId) {
        fetch(`/tasks/${taskId}/accept`, { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert('Задание принято! После проверки мандарины поступят на холд.');
                    // Закрыть модалку
                    document.querySelector('[x-data]').__x.$data.showModal = false;
                } else {
                    alert('Ошибка: ' + data.error);
                }
            });
    };
});