document.addEventListener('DOMContentLoaded', () => {
    let employeesData = [];
    let filteredData = [];
    let selectedEmployeeIds = new Set();
    let currentPage = 1;
    const itemsPerPage = 3;
    let currentSortColumn = null;
    let sortDirection = 'asc'; // 'asc' или 'desc'

    const tableBody = document.getElementById('table-body');
    const selectAllCheckbox = document.getElementById('select-all');
    const loader = document.getElementById('loader');
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const toggleFormBtn = document.getElementById('toggle-form-btn');
    const formContainer = document.getElementById('form-container');
    const paginationContainer = document.getElementById('pagination-container');
    const detailsBlock = document.getElementById('details-block');
    const detailsContent = document.getElementById('details-content');
    const bonusBlock = document.getElementById('bonus-block');
    const bonusContent = document.getElementById('bonus-content');

    // Элементы формы
    const fullNameInput = document.getElementById('inp-fullname');
    const inpUrl = document.getElementById('inp-url');
    const inpPhone = document.getElementById('inp-phone');
    const emailInput = document.getElementById('inp-email');
    const submitBtn = document.getElementById('submit-btn');
    const errUrl = document.getElementById('err-url');
    const errPhone = document.getElementById('err-phone');
    const addForm = document.getElementById('add-employee-form');

    const loaderText = loader ? loader.querySelector('.furn-loader__text') : null;

    function setLoading(isLoading, message = 'Загрузка данных...') {
        if (!loader) return;
        if (loaderText && message) {
            loaderText.textContent = message;
        }
        loader.style.display = isLoading ? 'flex' : 'none';
    }

    function runWithLoader(action, message = 'Выполнение операции...', delayMs = 1500) {
        setLoading(true, message);

        const finish = () => {
            try {
                action();
            } finally {
                setLoading(false);
            }
        };

        // Небольшая задержка нужна, чтобы браузер успел отрисовать прелоадер
        // даже при быстрой клиентской обработке массива
        if (delayMs > 0) {
            setTimeout(finish, delayMs);
        } else {
            finish();
        }
    }

    function updateSelectAllState() {
        if (!selectAllCheckbox || !tableBody) return;
        const pageCheckboxes = tableBody.querySelectorAll('.row-checkbox');
        if (pageCheckboxes.length === 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
            return;
        }
        const checkedCount = Array.from(pageCheckboxes).filter(cb => cb.checked).length;
        selectAllCheckbox.checked = checkedCount === pageCheckboxes.length;
        selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < pageCheckboxes.length;
    }

    // 1. Загрузка данных с сервера с прелоадером
    function fetchEmployees() {
        setLoading(true, 'Загрузка данных...');
        fetch('/api/employees/')
            .then(response => {
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return response.json();
            })
            .then(data => {
                employeesData = data.employees || [];
                filteredData = [...employeesData];
                renderTable();
            })
            .catch(error => {
                console.error('Ошибка загрузки:', error);
            })
            .finally(() => {
                setLoading(false);
            });
    }

    fetchEmployees();

    // 2. Отображение таблицы и пагинация
    function renderTable() {
        if (!tableBody) return;
        tableBody.innerHTML = '';
        const start = (currentPage - 1) * itemsPerPage;
        const end = start + itemsPerPage;
        const paginatedItems = filteredData.slice(start, end);

        if (paginatedItems.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="6" style="text-align: center;">Нет данных</td></tr>`;
            if (paginationContainer) paginationContainer.innerHTML = '';
            updateSelectAllState();
            return;
        }

        paginatedItems.forEach(emp => {
            const empId = String(emp.id);
            const tr = document.createElement('tr');
            tr.dataset.id = emp.id;
            tr.innerHTML = `
                <td><input type="checkbox" class="row-checkbox" data-id="${emp.id}" data-name="${emp.full_name}"></td>
                <td>${emp.full_name}</td>
                <td>${emp.photo ? `<img src="${emp.photo}" width="50" style="border-radius:4px;">` : 'Нет фото'}</td>
                <td>${emp.description}</td>
                <td>${emp.phone}</td>
                <td>${emp.email}</td>
            `;

            const checkbox = tr.querySelector('.row-checkbox');
            if (checkbox) {
                checkbox.checked = selectedEmployeeIds.has(empId);
                checkbox.addEventListener('change', (e) => {
                    e.stopPropagation();
                    if (checkbox.checked) {
                        selectedEmployeeIds.add(empId);
                    } else {
                        selectedEmployeeIds.delete(empId);
                    }
                    updateSelectAllState();
                });
            }

            tr.addEventListener('click', (e) => {
                if (e.target.tagName === 'INPUT') return;
                showDetails(emp);
            });

            tableBody.appendChild(tr);
        });

        updateSelectAllState();
        renderPagination();
    }

    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', () => {
            if (!tableBody) return;
            const pageCheckboxes = tableBody.querySelectorAll('.row-checkbox');
            pageCheckboxes.forEach(cb => {
                cb.checked = selectAllCheckbox.checked;
                const empId = String(cb.dataset.id);
                if (selectAllCheckbox.checked) {
                    selectedEmployeeIds.add(empId);
                } else {
                    selectedEmployeeIds.delete(empId);
                }
            });
            selectAllCheckbox.indeterminate = false;
        });
    }

    function renderPagination() {
        if (!paginationContainer) return;
        paginationContainer.innerHTML = '';
        const totalPages = Math.ceil(filteredData.length / itemsPerPage);
        if (totalPages <= 1) return;

        for (let i = 1; i <= totalPages; i++) {
            const btn = document.createElement('button');
            btn.textContent = i;
            if (i === currentPage) btn.classList.add('active');
            btn.addEventListener('click', () => {
                currentPage = i;
                renderTable();
            });
            paginationContainer.appendChild(btn);
        }
    }

    // 3. Фильтрация
    if (searchBtn && searchInput) {
        searchBtn.addEventListener('click', () => {
            const query = searchInput.value.toLowerCase().trim();
            runWithLoader(() => {
                if (!query) {
                    filteredData = [...employeesData];
                } else {
                    const searchableFields = ['full_name', 'description', 'phone', 'email'];
                    filteredData = employeesData.filter(emp =>
                        searchableFields.some(field =>
                            String(emp[field] || '').toLowerCase().includes(query)
                        )
                    );
                }
                currentPage = 1;
                renderTable();
            }, 'Фильтрация записей...', 200);
        });
    }

    // 4. Сортировка по столбцам
    document.querySelectorAll('th[data-sort]').forEach(th => {
        th.addEventListener('click', () => {
            const column = th.dataset.sort;
            if (currentSortColumn === column) {
                sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                currentSortColumn = column;
                sortDirection = 'asc';
            }

            document.querySelectorAll('.sort-indicator').forEach(el => el.textContent = '');
            const indicator = th.querySelector('.sort-indicator');
            if (indicator) indicator.textContent = sortDirection === 'asc' ? '▲' : '▼';

            filteredData.sort((a, b) => {
                let valA = a[column] || '';
                let valB = b[column] || '';
                if (valA < valB) return sortDirection === 'asc' ? -1 : 1;
                if (valA > valB) return sortDirection === 'asc' ? 1 : -1;
                return 0;
            });

            renderTable();
        });
    });

    // 5. Показ деталей строки под таблицей
    function showDetails(emp) {
        if (!detailsBlock || !detailsContent) return;
        detailsBlock.style.display = 'block';
        detailsContent.innerHTML = `
            <strong>ФИО:</strong> ${emp.full_name}<br>
            <strong>Должность / Работы:</strong> ${emp.description}<br>
            <strong>Телефон:</strong> ${emp.phone}<br>
            <strong>Email:</strong> ${emp.email}<br>
            ${emp.photo ? `<img src="${emp.photo}" width="100" style="margin-top:10px; border-radius:4px;">` : ''}
        `;
    }

    // 6. Валидация URL и Телефона
    function validateUrl(url) {
        const regex = /^https?:\/\/.+\.(php|html)$/i;
        return regex.test(url);
    }

    function validatePhone(phone) {
        const regex = /^(\+375|8)\s*\(?\d{2}\)?\s*\d{3}[\s-]?\d{2}[\s-]?\d{2}$/;
        return regex.test(phone);
    }

    function checkFormValidity() {
        if (!inpUrl || !inpPhone || !submitBtn) return;
        const isUrlValid = validateUrl(inpUrl.value.trim());
        const isPhoneValid = validatePhone(inpPhone.value.trim());

        if (inpUrl.value && !isUrlValid) {
            inpUrl.classList.add('input-error');
            if (errUrl) errUrl.textContent = 'Неверный формат URL. Пример: http://site.ru/index.php';
        } else {
            inpUrl.classList.remove('input-error');
            if (errUrl) errUrl.textContent = '';
        }

        if (inpPhone.value && !isPhoneValid) {
            inpPhone.classList.add('input-error');
            if (errPhone) errPhone.textContent = 'Неверный формат телефона. Пример: +375 (29) 111-22-33';
        } else {
            inpPhone.classList.remove('input-error');
            if (errPhone) errPhone.textContent = '';
        }

        const hasName = fullNameInput && fullNameInput.value.trim().length > 0;
        const hasEmail = emailInput && emailInput.value.trim().length > 0;

        if (isUrlValid && isPhoneValid && hasName && hasEmail) {
            submitBtn.removeAttribute('disabled');
        } else {
            submitBtn.setAttribute('disabled', 'true');
        }
    }

    if (inpUrl) inpUrl.addEventListener('input', checkFormValidity);
    if (inpPhone) inpPhone.addEventListener('input', checkFormValidity);
    if (fullNameInput) fullNameInput.addEventListener('input', checkFormValidity);
    if (emailInput) emailInput.addEventListener('input', checkFormValidity);

    if (toggleFormBtn && formContainer) {
        toggleFormBtn.addEventListener('click', () => {
            formContainer.classList.toggle('active');
        });
    }

    if (addForm) {
        addForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const newEmp = {
                id: Date.now(),
                full_name: fullNameInput ? fullNameInput.value.trim() : '',
                photo: '',
                description: 'Новый сотрудник (' + inpUrl.value.trim() + ')',
                phone: inpPhone.value.trim(),
                email: emailInput ? emailInput.value.trim() : ''
            };

            runWithLoader(() => {
                employeesData.unshift(newEmp);
                filteredData = [...employeesData];
                currentPage = 1;
                renderTable();
                addForm.reset();
                submitBtn.setAttribute('disabled', 'true');
                if (formContainer) formContainer.classList.remove('active');
            }, 'Добавление сотрудника...', 200);
        });
    }

    // 7. Кнопка премирования выбранных чекбоксами (по всем страницам)
    const premiateBtn = document.getElementById('premiate-btn');
    if (premiateBtn) {
        premiateBtn.addEventListener('click', () => {
            const selectedEmployees = employeesData.filter(emp =>
                selectedEmployeeIds.has(String(emp.id))
            );

            if (selectedEmployees.length === 0) {
                alert('Выберите хотя бы одного сотрудника для премирования!');
                return;
            }

            runWithLoader(() => {
                const names = selectedEmployees.map(emp => emp.full_name);
                if (bonusBlock && bonusContent) {
                    bonusBlock.style.display = 'block';
                    bonusContent.innerHTML = `Приказываю выдать премию следующим сотрудникам: <strong>${names.join(', ')}</strong> за успешное выполнение текущих задач и высокий профессионализм.`;
                }
            }, 'Формирование приказа о премировании...', 200);
        });
    }
});