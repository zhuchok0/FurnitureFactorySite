document.addEventListener('DOMContentLoaded', () => {

    // --- Генератор элементов формы ---
    const STORAGE_KEY = 'customCheckboxElements_v1';
    const OPEN_STATE_KEY = 'customCheckboxSectionOpen_v1';

    const generateTrigger = document.getElementById('generate-checkbox-trigger');
    const generatedWorkspace = document.getElementById('generated-workspace');
    const addGeneratedBtn = document.getElementById('add-generated-checkbox-btn');
    const generatedList = document.getElementById('generated-checkboxes-list');
    const deleteSelectedBtn = document.getElementById('delete-selected-generated-btn');

    let generatedItems = [];
    let selectedGeneratedIds = new Set();

    function loadGeneratedItems() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            const parsed = raw ? JSON.parse(raw) : [];
            generatedItems = Array.isArray(parsed) ? parsed : [];
        } catch (err) {
            console.error('Ошибка чтения сгенерированных элементов из localStorage:', err);
            generatedItems = [];
        }
    }

    function saveGeneratedItems() {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(generatedItems));
        } catch (err) {
            console.error('Ошибка сохранения сгенерированных элементов в localStorage:', err);
        }
    }

    function saveWorkspaceVisibility(isOpen) {
        try {
            localStorage.setItem(OPEN_STATE_KEY, isOpen ? '1' : '0');
        } catch (err) {
            console.error('Ошибка сохранения состояния переключателя:', err);
        }
    }

    function applyWorkspaceVisibility(isOpen) {
        if (generateTrigger) {
            generateTrigger.checked = Boolean(isOpen);
        }
        if (generatedWorkspace) {
            generatedWorkspace.style.display = isOpen ? 'block' : 'none';
        }
    }

    function updateDeleteSelectedButton() {
        if (!deleteSelectedBtn) return;
        deleteSelectedBtn.disabled = selectedGeneratedIds.size === 0;
    }

    function applyCheckboxAttributes(inputEl, item) {
        if (item.name) {
            inputEl.setAttribute('name', item.name);
            inputEl.name = item.name;
        } else {
            inputEl.removeAttribute('name');
            inputEl.name = '';
        }

        inputEl.setAttribute('value', item.value);
        inputEl.value = item.value;

        inputEl.defaultChecked = Boolean(item.checked);
        inputEl.checked = Boolean(item.checked);
        if (item.checked) {
            inputEl.setAttribute('checked', 'checked');
        } else {
            inputEl.removeAttribute('checked');
        }

        inputEl.required = Boolean(item.required);
        if (item.required) {
            inputEl.setAttribute('required', 'required');
        } else {
            inputEl.removeAttribute('required');
        }

        inputEl.disabled = Boolean(item.disabled);
        if (item.disabled) {
            inputEl.setAttribute('disabled', 'disabled');
        } else {
            inputEl.removeAttribute('disabled');
        }
    }

    function createGeneratedItem() {
        const index = generatedItems.length + 1;
        const newItem = {
            id: `cb_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
            name: `checkbox_${index}`,
            value: `value_${index}`,
            checked: false,
            required: false,
            disabled: false
        };
        generatedItems.push(newItem);
        saveGeneratedItems();
        renderGeneratedItems();
    }
  
    function deleteGeneratedItem(id) {
        generatedItems = generatedItems.filter(item => item.id !== id);
        selectedGeneratedIds.delete(id);
        saveGeneratedItems();
        renderGeneratedItems();
    }

    function renderGeneratedItems() {
        if (!generatedList) return;
        generatedList.innerHTML = '';

        const existingIds = new Set(generatedItems.map(item => item.id));
        selectedGeneratedIds = new Set(
            Array.from(selectedGeneratedIds).filter(id => existingIds.has(id))
        );

        if (generatedItems.length === 0) {
            generatedList.innerHTML = '<p>Сгенерированных флажков пока нет. Нажмите «+ Добавить элемент», чтобы создать первый.</p>';
            updateDeleteSelectedButton();
            return;
        }

        generatedItems.forEach((item, idx) => {
            const card = document.createElement('div');
            card.className = 'generated-item-card';
            card.dataset.id = item.id;

            const header = document.createElement('div');
            header.className = 'generated-item-header';

            const selectLabel = document.createElement('label');
            selectLabel.className = 'generated-item-select';

            const selectCheckbox = document.createElement('input');
            selectCheckbox.type = 'checkbox';
            selectCheckbox.checked = selectedGeneratedIds.has(item.id);
            selectCheckbox.addEventListener('change', () => {
                if (selectCheckbox.checked) {
                    selectedGeneratedIds.add(item.id);
                } else {
                    selectedGeneratedIds.delete(item.id);
                }
                updateDeleteSelectedButton();
            });

            const titleSpan = document.createElement('span');
            titleSpan.textContent = `Элемент #${idx + 1}`;

            selectLabel.appendChild(selectCheckbox);
            selectLabel.appendChild(titleSpan);

            const deleteBtn = document.createElement('button');
            deleteBtn.type = 'button';
            deleteBtn.className = 'btn-delete-item';
            deleteBtn.textContent = 'Удалить';
            deleteBtn.addEventListener('click', () => deleteGeneratedItem(item.id));

            header.appendChild(selectLabel);
            header.appendChild(deleteBtn);

            const preview = document.createElement('div');
            preview.className = 'generated-item-preview';

            const generatedCheckbox = document.createElement('input');
            generatedCheckbox.type = 'checkbox';
            applyCheckboxAttributes(generatedCheckbox, item);

            const previewMeta = document.createElement('span');
            const updatePreviewMeta = () => {
                previewMeta.textContent =
                    `name="${item.name}" | value="${item.value}" | ` +
                    `checked=${item.checked} | required=${item.required} | disabled=${item.disabled}`;
            };

            generatedCheckbox.addEventListener('change', () => {
                item.checked = generatedCheckbox.checked;
                checkedInput.checked = item.checked;
                if (item.checked) {
                    generatedCheckbox.setAttribute('checked', 'checked');
                } else {
                    generatedCheckbox.removeAttribute('checked');
                }
                updatePreviewMeta();
                saveGeneratedItems();
            });

            updatePreviewMeta();
            preview.appendChild(generatedCheckbox);
            preview.appendChild(previewMeta);

            const attrsGrid = document.createElement('div');
            attrsGrid.className = 'generated-item-attrs';

            const nameLabel = document.createElement('label');
            nameLabel.textContent = 'Атрибут name:';
            const nameInput = document.createElement('input');
            nameInput.type = 'text';
            nameInput.value = item.name;
            nameInput.addEventListener('input', () => {
                item.name = nameInput.value;
                applyCheckboxAttributes(generatedCheckbox, item);
                updatePreviewMeta();
                saveGeneratedItems();
            });
            nameLabel.appendChild(nameInput);

            const valueLabel = document.createElement('label');
            valueLabel.textContent = 'Атрибут value:';
            const valueInput = document.createElement('input');
            valueInput.type = 'text';
            valueInput.value = item.value;
            valueInput.addEventListener('input', () => {
                item.value = valueInput.value;
                applyCheckboxAttributes(generatedCheckbox, item);
                updatePreviewMeta();
                saveGeneratedItems();
            });
            valueLabel.appendChild(valueInput);

            const checkedLabel = document.createElement('label');
            checkedLabel.className = 'attr-bool-label';
            const checkedInput = document.createElement('input');
            checkedInput.type = 'checkbox';
            checkedInput.checked = Boolean(item.checked);
            checkedInput.addEventListener('change', () => {
                item.checked = checkedInput.checked;
                applyCheckboxAttributes(generatedCheckbox, item);
                updatePreviewMeta();
                saveGeneratedItems();
            });
            checkedLabel.appendChild(checkedInput);
            checkedLabel.appendChild(document.createTextNode('checked'));

            const requiredLabel = document.createElement('label');
            requiredLabel.className = 'attr-bool-label';
            const requiredInput = document.createElement('input');
            requiredInput.type = 'checkbox';
            requiredInput.checked = Boolean(item.required);
            requiredInput.addEventListener('change', () => {
                item.required = requiredInput.checked;
                applyCheckboxAttributes(generatedCheckbox, item);
                updatePreviewMeta();
                saveGeneratedItems();
            });
            requiredLabel.appendChild(requiredInput);
            requiredLabel.appendChild(document.createTextNode('required'));

            const disabledLabel = document.createElement('label');
            disabledLabel.className = 'attr-bool-label';
            const disabledInput = document.createElement('input');
            disabledInput.type = 'checkbox';
            disabledInput.checked = Boolean(item.disabled);
            disabledInput.addEventListener('change', () => {
                item.disabled = disabledInput.checked;
                applyCheckboxAttributes(generatedCheckbox, item);
                updatePreviewMeta();
                saveGeneratedItems();
            });
            disabledLabel.appendChild(disabledInput);
            disabledLabel.appendChild(document.createTextNode('disabled'));

            attrsGrid.appendChild(nameLabel);
            attrsGrid.appendChild(valueLabel);
            attrsGrid.appendChild(checkedLabel);
            attrsGrid.appendChild(requiredLabel);
            attrsGrid.appendChild(disabledLabel);

            card.appendChild(header);
            card.appendChild(preview);
            card.appendChild(attrsGrid);
            generatedList.appendChild(card);
        });

        updateDeleteSelectedButton();
    }

    if (generateTrigger) {
        generateTrigger.addEventListener('change', () => {
            const isOpen = generateTrigger.checked;
            applyWorkspaceVisibility(isOpen);
            saveWorkspaceVisibility(isOpen);
        });
    }

    if (addGeneratedBtn) {
        addGeneratedBtn.addEventListener('click', createGeneratedItem);
    }

    if (deleteSelectedBtn) {
        deleteSelectedBtn.addEventListener('click', () => {
            if (selectedGeneratedIds.size === 0) return;
            generatedItems = generatedItems.filter(item => !selectedGeneratedIds.has(item.id));
            selectedGeneratedIds.clear();
            saveGeneratedItems();
            renderGeneratedItems();
        });
    }

    loadGeneratedItems();
    renderGeneratedItems();
    const savedOpenState = localStorage.getItem(OPEN_STATE_KEY) === '1';
    applyWorkspaceVisibility(savedOpenState);

    // ---------- Таблица сотрудников ------------------

    let employeesData = [];
    let filteredData = [];
    let selectedEmployeeIds = new Set();
    let currentPage = 1;
    const itemsPerPage = 3;
    let currentSortColumn = null;
    let sortDirection = 'asc';

    const tableBody = document.getElementById('table-body');
    const selectAllCheckbox = document.getElementById('select-all');
    const loader = document.getElementById('loader');
    
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const premiateBtn = document.getElementById('premiate-btn');
    const toggleFormBtn = document.getElementById('toggle-form-btn');

    const formContainer = document.getElementById('form-container');
    const paginationContainer = document.getElementById('pagination-container');
    const detailsBlock = document.getElementById('details-block');
    const detailsContent = document.getElementById('details-content');
    const bonusBlock = document.getElementById('bonus-block');
    const bonusContent = document.getElementById('bonus-content');

    const fullNameInput = document.getElementById('inp-fullname');
    const inpUrl = document.getElementById('inp-url');
    const inpPhone = document.getElementById('inp-phone');
    const emailInput = document.getElementById('inp-email');
    const submitBtn = document.getElementById('submit-btn');
    const errUrl = document.getElementById('err-url');
    const errPhone = document.getElementById('err-phone');
    const addForm = document.getElementById('add-employee-form');

    const inpPhoto = document.getElementById('inp-photo');
    const errPhoto = document.getElementById('err-photo');
    const EMP_STORAGE_KEY = 'customEmployees_v1';
    const MAX_PHOTO_SIZE = 5 * 1024 * 1024; 
    const PHOTO_MAX_SIDE = 300;

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

    function loadCustomEmployees() {
        try {
            const raw = localStorage.getItem(EMP_STORAGE_KEY);
            const parsed = raw ? JSON.parse(raw) : [];
            return Array.isArray(parsed) ? parsed : [];
        } catch (err) {
            console.error('Ошибка чтения сотрудников из localStorage:', err);
            return [];
        }
    }

    function saveCustomEmployees(list) {
        try {
            localStorage.setItem(EMP_STORAGE_KEY, JSON.stringify(list));
            return true;
        } catch (err) {
            console.error('Ошибка сохранения сотрудников в localStorage:', err);
            return false;
        }
    }

    function getPhotoFile() {
        return inpPhoto && inpPhoto.files ? inpPhoto.files[0] : null;
    }

    function isPhotoValid(file) {
        return !!file && file.type.startsWith('image/') && file.size <= MAX_PHOTO_SIZE;
    }

    function resizePhoto(file) {
        return new Promise((resolve, reject) => {
            const url = URL.createObjectURL(file);
            const img = new Image();
            img.onload = () => {
                const scale = Math.min(1, PHOTO_MAX_SIDE / Math.max(img.width, img.height));
                const canvas = document.createElement('canvas');
                canvas.width = Math.round(img.width * scale);
                canvas.height = Math.round(img.height * scale);
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = '#ffffff';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                URL.revokeObjectURL(url);
                resolve(canvas.toDataURL('image/jpeg', 0.8));
            };
            img.onerror = () => {
                URL.revokeObjectURL(url);
                reject(new Error('Не удалось прочитать изображение.'));
            };
            img.src = url;
        });
    }

    function fetchEmployees() {
        setLoading(true, 'Загрузка данных...');
        fetch('/api/employees/')
            .then(response => {
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return response.json();
            })
            .then(data => {
                employeesData = [...loadCustomEmployees(), ...(data.employees || [])];
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

    function validateUrl(url) {
        const regex = /^https?:\/\/.+\.(php|html)$/i;
        return regex.test(url);
    }

    function validatePhone(phone) {
        const regex = /^(?:\+375\s*\(?\d{2}\)?|8\s*\(?0\d{2}\)?)\s*\d{3}[\s-]?\d{2}[\s-]?\d{2}$/;
        return regex.test(phone);
    }

    function checkFormValidity() {
        if (!inpUrl || !inpPhone || !submitBtn) return;
        const isUrlValid = validateUrl(inpUrl.value.trim());
        const isPhoneValid = validatePhone(inpPhone.value.trim());

        if (inpUrl.value && !isUrlValid) {
            inpUrl.classList.add('input-error');
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

        const photoFile = getPhotoFile();
        const isPhotoOk = isPhotoValid(photoFile);
        if (photoFile && !isPhotoOk) {
            if (inpPhoto) inpPhoto.classList.add('input-error');
            if (errPhoto) errPhoto.textContent = 'Выберите изображение размером до 5 МБ';
        } else {
            if (inpPhoto) inpPhoto.classList.remove('input-error');
            if (errPhoto) errPhoto.textContent = '';
        }

        const hasName = fullNameInput && fullNameInput.value.trim().length > 0;
        const hasEmail = emailInput && emailInput.value.trim().length > 0;

        if (isUrlValid && isPhoneValid && hasName && hasEmail && isPhotoOk) {
            submitBtn.removeAttribute('disabled');
        } else {
            submitBtn.setAttribute('disabled', 'true');
        }
    }

    if (inpUrl) inpUrl.addEventListener('input', checkFormValidity);
    if (inpPhone) inpPhone.addEventListener('input', checkFormValidity);
    if (fullNameInput) fullNameInput.addEventListener('input', checkFormValidity);
    if (emailInput) emailInput.addEventListener('input', checkFormValidity);
    if (inpPhoto) inpPhoto.addEventListener('change', checkFormValidity);

    if (toggleFormBtn && formContainer) {
        toggleFormBtn.addEventListener('click', () => {
            formContainer.classList.toggle('active');
        });
    }

    if (addForm) {
        addForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const photoFile = getPhotoFile();
            if (!isPhotoValid(photoFile)) return;

            if (errPhoto) errPhoto.textContent = '';
            submitBtn.setAttribute('disabled', 'true');

            resizePhoto(photoFile)
                .then((photoData) => {
                    const newEmp = {
                        id: 'local_' + Date.now(),
                        full_name: fullNameInput ? fullNameInput.value.trim() : '',
                        photo: photoData,
                        description: 'Новый сотрудник (' + inpUrl.value.trim() + ')',
                        phone: inpPhone.value.trim(),
                        email: emailInput ? emailInput.value.trim() : ''
                    };

                    const custom = loadCustomEmployees();
                    custom.unshift(newEmp);
                    if (!saveCustomEmployees(custom)) {
                        if (errPhoto) errPhoto.textContent = 'Не удалось сохранить: хранилище браузера переполнено или недоступно.';
                        checkFormValidity();
                        return;
                    }

                    runWithLoader(() => {
                        employeesData.unshift(newEmp);
                        filteredData = [...employeesData];
                        currentPage = 1;
                        renderTable();
                        addForm.reset();
                        submitBtn.setAttribute('disabled', 'true');
                        if (formContainer) formContainer.classList.remove('active');
                    }, 'Добавление сотрудника...', 200);
                })
                .catch((err) => {
                    if (errPhoto) errPhoto.textContent = err.message;
                    checkFormValidity();
                });
        });
    }

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
                    bonusContent.innerHTML = `Премия будет выдана следующим сотрудникам: <strong>${names.join(', ')}</strong> за успешное выполнение текущих задач и высокий профессионализм.`;
                }
            }, 'Формирование приказа о премировании...', 200);
        });
    }
});