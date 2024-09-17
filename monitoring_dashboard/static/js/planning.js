document.addEventListener("DOMContentLoaded", function() {
    const content = document.querySelector('.content');
    content.style.opacity = 0;
    content.style.transition = 'opacity 2s';
    setTimeout(() => {
        content.style.opacity = 1;
    }, 100);

    const sidebarLinks = document.querySelectorAll('.sidebar ul li');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function() {
            sidebarLinks.forEach(link => link.classList.remove('active'));
            this.classList.add('active');
        });
    });

    const monthSelect = document.getElementById("monthSelect");
    const yearSelect = document.getElementById("yearSelect");
    const editScheduleButton = document.getElementById("editScheduleButton");
    const todayButton = document.getElementById("todayButton");
    const calendarBody = document.querySelector("#calendar tbody");
    const modal = document.getElementById("modal");
    const closeButton = document.querySelector(".close");
    const scheduleForm = document.getElementById("scheduleForm");
    const tooltip = document.getElementById('tooltip');
    const detailsModal = document.getElementById("detailsModal");
    const closeDetailsModalButton = detailsModal.querySelector(".close");
    const eventDetails = document.getElementById("eventDetails");
    

    const eventColors = {
        work: "#1e536e",
        holiday: "#f0ad4e",
        meeting: "#d9534f",
    };

    let events = {};

    async function fetchScheduleDetails(ids) {
        try {
            const response = await fetch('/get-schedule-calendarcell-urgent/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest' // Indicates AJAX request
                },
                body: JSON.stringify({ schedule_ids: ids }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok: ' + response.statusText);
            }

            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }

            return data;
        } catch (error) {
            console.error('Error fetching schedule details:', error);
            return [];
        }
    }

    function extractIdsFromDetails(details) {
        const regex = /Идентификатор:\s*(\d+)/g;
        const ids = [];
        let match;
        while ((match = regex.exec(details)) !== null) {
            ids.push(parseInt(match[1]));
        }
        return ids;
    }

    function openDetailsModal(details) {
        const ids = extractIdsFromDetails(details);
        fetchScheduleDetails(ids)
            .then(fetchedDetails => {
                eventDetails.innerHTML = '';
                if (!fetchedDetails || fetchedDetails.length === 0) {
                    console.error('No details found');
                    return;
                }

                fetchedDetails.forEach(detail => {
                    const detailDiv = document.createElement('div');
                    detailDiv.className = 'schedule-detail';

                    detailDiv.innerHTML = `
                        <strong>${detail.productType}</strong><br>
                        Идентификатор: ${detail.ID}<br>
                        Количество: ${detail.quantity}<br>
                        Номер заказа: ${detail.orderNum}<br>
                        ЛИМЦ: ${detail.limtz}<br>
                        Оператор: ${detail.operatorName}<br>
                        Станок с ЧПУ: ${detail.cncMachine.name}<br>
                    `;

                    if (detail.urgent) {
                        detailDiv.classList.add('urgent');
                        const urgentIndicator = document.createElement('div');
                        urgentIndicator.className = 'urgent-indicator';
                        urgentIndicator.innerHTML = `<i class="fas fa-bell" style="color: red;"></i> Срочно!`;
                        detailDiv.appendChild(urgentIndicator);
                    } else {
                        detailDiv.classList.add('normal');
                    }

                    eventDetails.appendChild(detailDiv);
                });

                detailsModal.classList.add("show");
                detailsModal.querySelector(".custom-details-modal-content").classList.add("show");
            })
            .catch(error => console.error('Error fetching schedule details:', error));
    }

    function closeDetailsModal() {
        detailsModal.classList.remove("show");
        detailsModal.querySelector(".custom-details-modal-content").classList.remove("show");
    }

    closeDetailsModalButton.addEventListener("click", closeDetailsModal);
    window.addEventListener("click", function(event) {
        if (event.target == detailsModal) {
            closeDetailsModal();
        }
    });

    function generateCalendar(month, year) {
        calendarBody.innerHTML = "";
    
        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const totalCells = 42; // 6 weeks x 7 days
    
        let date = 1;
    
        for (let i = 0; i < 6; i++) { // 6 rows
            const row = document.createElement("tr");
    
            for (let j = 0; j < 7; j++) { // 7 days
                const cell = document.createElement("td");
    
                if (i === 0 && j < firstDay) {
                    // Cells before the first day of the month
                    cell.classList.add('empty');
                } else if (date <= daysInMonth) {
                    // Cells with days of the current month
                    cell.appendChild(document.createTextNode(date));
    
                    const eventKey = `${year}-${month + 1}-${date}`;
    
                    if (events[eventKey]) {
                        const eventDiv = document.createElement("div");
                        eventDiv.className = `event`;
                        eventDiv.style.backgroundColor = '#1a334a'; // background for the small action bar in each cell
                        eventDiv.textContent = `${events[eventKey].length} Действия`;
                        cell.appendChild(eventDiv);
                        // cell.style.backgroundColor = '#243c44'; // Background of the cells which have actions in them
                        cell.style.backgroundColor = '#1f1f1f'; // Background of the cells which have actions in them
                    }
    
                    cell.addEventListener('mouseenter', function(event) {
                        if (events[eventKey]) {
                            tooltip.innerHTML = events[eventKey].map(event => `
                                <strong>${event.productType}</strong><br>
                                Идентификатор: ${event.ID}<br>
                                Количество: ${event.quantity}<br>
                                Оператор: ${event.operatorName}<br>
                                Станок с ЧПУ: ${event.cncMachine}
                            `).join('<br><br>');
                            tooltip.style.display = 'block';
                            tooltip.style.left = `${event.pageX + 10}px`;
                            tooltip.style.top = `${event.pageY + 10}px`;
                        }
                        // cell.style.backgroundColor = '#41737a';
                        cell.style.backgroundColor = '#444444';
                    });
    
                    cell.addEventListener('mouseleave', function() {
                        tooltip.style.display = 'none';
                        // cell.style.backgroundColor = events[eventKey] ? '#243c44' : '#243c44';
                        cell.style.backgroundColor = events[eventKey] ? '#1f1f1f' : '#252525';
                    });
    
                    cell.addEventListener('mousemove', function(event) {
                        tooltip.style.left = `${event.pageX + 10}px`;
                        tooltip.style.top = `${event.pageY + 10}px`;
                    });
    
                    cell.addEventListener('click', function() {
                        if (events[eventKey]) {
                            const details = events[eventKey].map(event => `
                                <strong>${event.productType}</strong><br>
                                Идентификатор: ${event.ID}<br>
                                Количество: ${event.quantity}<br>
                                Оператор: ${event.operatorName}<br>
                                Станок с ЧПУ: ${event.cncMachine}
                            `).join('<br><br>');
                            openDetailsModal(details);
                        }
                    });
    
                    date++;
                } else {
                    // Cells after the last day of the month
                    cell.classList.add('empty');
                }
    
                row.appendChild(cell);
            }
    
            calendarBody.appendChild(row);
        }
    }

    function populateSelectElements() {
        const months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"];
        const now = new Date();

        months.forEach((month, index) => {
            const option = document.createElement("option");
            option.value = index;
            option.textContent = month;
            monthSelect.appendChild(option);
        });

        for (let i = now.getFullYear() - 10; i <= now.getFullYear() + 10; i++) {
            const option = document.createElement("option");
            option.value = i;
            option.textContent = i;
            yearSelect.appendChild(option);
        }

        monthSelect.value = now.getMonth();
        yearSelect.value = now.getFullYear();
    }

    function showToday() {
        const now = new Date();
        monthSelect.value = now.getMonth();
        yearSelect.value = now.getFullYear();
        fetchAndGenerateCalendar(now.getMonth(), now.getFullYear());
    }

    function showModal() {
        populateOperatorSelect();
        populateCncMachineSelect();
        modal.style.display = "block";
    }

    function closeModal() {
        modal.style.display = "none";
    }

    // ===========> To also register the Order number and LIMTZ to the DB
    function addEvent(e) {
        e.preventDefault();
        const formData = new FormData(scheduleForm);
    
        fetch('/add-schedule/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'  // Set this to identify AJAX requests
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                closeModal();
                const startDate = formData.get("startDate");
                const endDate = formData.get("endDate");
                const [year, month] = startDate.split("-").map(Number);
                fetchAndGenerateCalendar(month - 1, year);
            } else {
                console.error('Не удалось добавить График:', data.error);
            }
        })
        .catch(error => {
            console.error('Error adding schedule:', error);
        });
    }
    
    scheduleForm.addEventListener("submit", addEvent);
    

    todayButton.addEventListener("click", showToday);
    editScheduleButton.addEventListener("click", showModal);
    closeButton.addEventListener("click", closeModal);
    window.addEventListener("click", function (event) {
        if (event.target == modal) {
            closeModal();
        }
    });

    scheduleForm.addEventListener("submit", addEvent);

    function fetchAndGenerateCalendar(month, year) {
        events = {};
        console.log(`Fetching schedule for month ${month + 1} and year ${year}`);
        fetch('/get-schedule/', {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest' // Indicates AJAX request
            }
        })
        .then(response => response.json())
        .then(data => {
            data.forEach(schedule => {
                const startDate = new Date(schedule.startDate);
                const endDate = new Date(schedule.endDate);

                endDate.setHours(23, 59, 59, 999);

                let currentDate = new Date(startDate);
                while (currentDate <= endDate) {
                    const eventKey = `${currentDate.getFullYear()}-${currentDate.getMonth() + 1}-${currentDate.getDate()}`;
                    if (!events[eventKey]) {
                        events[eventKey] = [];
                    }
                    events[eventKey].push({
                        event: "work",
                        ID: schedule.id,
                        productType: schedule.productType,
                        quantity: schedule.quantity,
                        operatorName: schedule.operatorName,
                        cncMachine: schedule.cncMachine.name,
                        startDate
                    });
                    currentDate.setDate(currentDate.getDate() + 1);
                }
            });
            generateCalendar(month, year);
        })
        .catch(error => console.error('Error fetching schedule:', error));
    }

    populateSelectElements();

    const now = new Date();
    fetchAndGenerateCalendar(now.getMonth(), now.getFullYear());

    monthSelect.addEventListener("change", () => {
        fetchAndGenerateCalendar(Number(monthSelect.value), Number(yearSelect.value));
    });

    yearSelect.addEventListener("change", () => {
        fetchAndGenerateCalendar(Number(monthSelect.value), Number(yearSelect.value));
    });

    function populateOperatorSelect() {
        fetch('/get-operators/', {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest' // Indicates AJAX request
            }
        })
            .then(response => response.json())
            .then(data => {
                const operatorSelect = document.getElementById('operatorSelect');
                operatorSelect.innerHTML = '';
                data.operators.forEach(operator => {
                    const option = document.createElement('option');
                    option.value = operator.username;
                    option.textContent = `${operator.username} - ${operator.full_name}`;
                    operatorSelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error fetching operators:', error));
    }

    function populateCncMachineSelect() {
        const cncMachineSelect = document.getElementById('cncMachine');

        fetch('/get_cnc_machines/', {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest' // Indicates AJAX request
            }
        })
            .then(response => response.json())
            .then(data => {
                cncMachineSelect.innerHTML = '';
                data.forEach(machine => {
                    const option = document.createElement('option');
                    option.value = machine.id;
                    option.textContent = machine.name;
                    cncMachineSelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error fetching CNC machines:', error));
    }

    populateSelectElements();

    // Chart.js setup for pie charts
    const ctxProduction = document.getElementById('productionVolumeChart').getContext('2d');
    new Chart(ctxProduction, {
        type: 'doughnut',
        data: {
            labels: ['Type A', 'Type B', 'Type C'],
            datasets: [{
                label: 'Production Volume',
                data: [12, 19, 7],
                backgroundColor: ['#53dfb5', '#ff949f', '#59c5f7'],
                borderColor: ['#3498db', '#e74c3c', '#2ecc71'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: {
                        fontfamily: "Rubik Mono One"
                    }
                }
            }
        }
    });

    const ctxDowntime = document.getElementById('downtimeChart').getContext('2d');
    new Chart(ctxDowntime, {
        type: 'bar',
        data: {
            labels: ['Maintenance', 'Technical', 'Operational'],
            datasets: [{
                label: 'Downtime',
                data: [2, 3, 1],
                backgroundColor: ['#e67e22', '#e74c3c', '#53dfb5'],
                borderColor: ['#e67e22', '#e74c3c', '#53dfb5'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            fontfamily: "Rubik Mono One",
            plugins: {
                legend: {
                    labels: {
                        fontfamily: "Rubik Mono One"
                    }
                }
            },
            aspectRatio: 1
        }
    });

    const ctxMachines = document.getElementById('machinesActiveChart').getContext('2d');
    new Chart(ctxMachines, {
        type: 'doughnut',
        data: {
            labels: ['Machine A', 'Machine B', 'Machine C'],
            datasets: [{
                label: 'Machines Active',
                data: [5, 7, 3],
                backgroundColor: ['#3498db', '#9b59b6', '#2ecc71'],
                borderColor: ['#2980b9', '#8e44ad', '#27ae60'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: {
                        fontfamily: "Rubik Mono One"
                    }
                }
            }
        }
    });
});

// Mechanism for adding the delete schedule

document.addEventListener("DOMContentLoaded", function() {
    const openDeleteFormButton = document.getElementById("openDeleteFormButton");
    const deleteModal = document.getElementById("deleteModal");
    const deleteForm = document.getElementById("deleteForm");
    const confirmDeleteButton = document.getElementById("confirmDeleteButton");
    const deleteDetails = document.getElementById("deleteDetails");
    const confirmYes = document.getElementById("confirmYes");
    const confirmNo = document.getElementById("confirmNo");
    const closeSpan = document.getElementsByClassName("close")[0];
    const confirmationMessage = document.getElementById("confirmationMessage");
    const scheduleDetails = document.getElementById("scheduleDetails");

    // Show the delete modal when the button is clicked
    openDeleteFormButton.addEventListener("click", function() {
        deleteModal.style.display = "block";
    });

    confirmDeleteButton.addEventListener("click", function() {
        const deleteId = document.getElementById("deleteId").value;

        fetch(`/get-schedule-details/`, {
            method: 'POST',
            body: JSON.stringify({ id: deleteId }),
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                deleteDetails.textContent = `Вы уверены, что хотите удалить это расписание? Идентификатор: ${data.schedule.ID}, Дата начала: ${data.schedule.startDate}, Дата окончания: ${data.schedule.endDate}, Тип продукта: ${data.schedule.productType}, Количество: ${data.schedule.quantity}, Оператор: ${data.schedule.operatorName}, Станок с ЧПУ: ${data.schedule.cncMachine.name}`;
                confirmationMessage.style.display = "block";
                scheduleDetails.style.display = "none";
            } else {
                alert('Schedule not found');
            }
        })
        .catch(error => {
            console.error('Error fetching schedule details:', error);
        });
    });

    confirmYes.addEventListener("click", function() {
        const deleteId = document.getElementById("deleteId").value;

        fetch(`/delete-schedule/`, {
            method: 'POST',
            body: JSON.stringify({ id: deleteId }),
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Schedule deleted successfully');
                deleteModal.style.display = "none";
                fetchAndGenerateCalendar(new Date().getMonth(), new Date().getFullYear());
            } else {
                alert('Failed to delete schedule');
            }
        })
        .catch(error => {
            console.error('Error deleting schedule:', error);
        });
    });

    confirmNo.addEventListener("click", function() {
        confirmationMessage.style.display = "none";
        scheduleDetails.style.display = "block";
    });

    closeSpan.addEventListener("click", function() {
        deleteModal.style.display = "none";
    });

    window.onclick = function(event) {
        if (event.target == deleteModal) {
            deleteModal.style.display = "none";
        }
    };

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Fetch and generate calendar (placeholder function, implement as needed)
    function fetchAndGenerateCalendar(month, year) {
        // Your existing code to fetch and generate the calendar
    }

    // Fetch the initial calendar
    fetchAndGenerateCalendar(new Date().getMonth(), new Date().getFullYear());
});


document.addEventListener("DOMContentLoaded", function() {
    const tableContainer = document.querySelector('.material-inventory');
    const headerCells = document.querySelectorAll('.table-header th');
    const bodyRows = document.querySelectorAll('planning-table tbody tr');

    if (bodyRows.length > 0) {
        const bodyCells = bodyRows[0].querySelectorAll('td');
        
        headerCells.forEach((headerCell, index) => {
            const bodyCellWidth = bodyCells[index].offsetWidth;
            headerCell.style.width = bodyCellWidth + 'px';
            bodyCells[index].style.width = bodyCellWidth + 'px'; // Ensure body cells have the same width
        });
    }

    tableContainer.addEventListener('scroll', function() {
        const scrollLeft = this.scrollLeft;
        document.querySelector('.table-header').style.transform = `translateX(${ -scrollLeft }px)`;
    });
});


document.addEventListener('DOMContentLoaded', () => {
    const filterButton = document.querySelector('.filter-button');
    const sortIcons = document.querySelectorAll('.sort-icon');

    filterButton.addEventListener('click', () => {
        alert('Filter button clicked!');
    });

    sortIcons.forEach(icon => {
        icon.addEventListener('click', () => {
            alert('Sort icon clicked!');
        });
    });
});

//  ==============> 2nd Version: Added modal functionality to change the table entries. <===================
document.addEventListener('DOMContentLoaded', function () {
    const deleteButton = document.getElementById('delete-from-db');
    const editButton = document.getElementById('edit-btn');
    const saveChangesButton = document.getElementById('saveChangesBtn');
    let $table = $('#table');
    let selections = [];

    function getIdSelections() {
        return $.map($table.bootstrapTable('getSelections'), function (row) {
            return row.id;
        });
    }

    function initializeRowListeners() {
        $table.on('check.bs.table uncheck.bs.table check-all.bs.table uncheck-all.bs.table', function () {
            const hasSelections = $table.bootstrapTable('getSelections').length > 0;
            deleteButton.disabled = !hasSelections;
            editButton.disabled = !hasSelections;
            selections = getIdSelections();
        });
    }

    deleteButton.addEventListener('click', function () {
        const idsToDelete = getIdSelections();
        const activeTab = document.querySelector('.tab-button.active').dataset.tab;

        if (idsToDelete.length === 0) {
            alert('Ни одна строка не выбрана для удаления.');
            return;
        }

        fetch('/delete_schedule_entries/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest' // Indicates AJAX request
            },
            body: JSON.stringify({ ids: idsToDelete, schedule: activeTab })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Entries deleted successfully!');
                $table.bootstrapTable('remove', {
                    field: 'id',
                    values: idsToDelete
                });
                deleteButton.disabled = true;
                editButton.disabled = true;
            } else {
                alert('Error deleting entries.');
            }
        })
        .catch(error => console.error('Error:', error));
    });

    editButton.addEventListener('click', function () {
        const selectedRow = $table.bootstrapTable('getSelections')[0];
        if (!selectedRow) {
            alert('Ни одна строка не выбрана для редактирования.');
            return;
        }
        showEditModal(selectedRow);
    });

    function showEditModal(row) {
        const activeTab = document.querySelector('.tab-button.active').dataset.tab;
        let formFields = `<input type="hidden" id="schedule" name="schedule" value="${activeTab}">
                          <input type="hidden" id="id" name="id" value="${row.id}">`;


        // Get column headers dynamically from the table
        const columns = $table.bootstrapTable('getOptions').columns[0];

        // // Exclude last two columns based on their 'field' attribute
        // const filteredColumns = columns.slice(0, -2); // Excludes the last two columns

        // Generate form fields based on filtered columns
        columns.forEach(column => {
            const key = column.field;
            const label = column.title;
            if (key !== 'id' && key !== 'state' && key !== 'checkbox') {
                formFields += `<div class="form-group">
                                <label for="${key}">${label}</label>
                                <input type="text" class="form-control" id="${key}" name="${key}" value="${row[key]}">
                            </div>`;
            }
        });

        $('#editForm').html(formFields);
        $('#editModal').modal('show');

        $('#editForm').off('submit').on('submit', function (event) {
            event.preventDefault();
            console.log("Form submitted");  // Debug statement
            const formData = $(this).serialize();

            console.log("Form Data:", formData);  // Debug statement

            $.ajax({
                url: '/update_production_schedule_data/',
                type: 'POST',
                data: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                success: function (response) {
                    console.log("Response:", response);  // Debug statement
                    if (response.success) {
                        alert('Entry updated successfully');
                        $('#editModal').modal('hide');
                        const activeTab = document.querySelector('.tab-button.active').dataset.tab;
                        loadTableData(activeTab);
                    } else {
                        alert('Failed to update entry');
                    }
                },
                error: function (error) {
                    console.error('Error:', error);
                    alert('Error updating entry');
                }
            });
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function loadTableData(schedule) {
        $('#table').bootstrapTable('destroy');
        $('#table').empty();

        $('#table').bootstrapTable({
            url: `/get_production_schedule_data?schedule=${schedule}`,
            columns: getColumns(schedule),
            search: true,
            pagination: true,
            showRefresh: true,
            showColumns: true,
            clickToSelect: true,
            showExport: true,
            onPostBody: function () {
                const shipmentColumnIndex = $('#table').bootstrapTable('getOptions').columns[0].findIndex(column => column.field === 'shipment');
                
                if (shipmentColumnIndex !== -1) {
                    $('#table').find('tbody tr').each(function () {
                        const cellValue = $(this).find(`td:nth-child(${shipmentColumnIndex + 1})`).text().trim();
                        if (cellValue) {
                            $(this).css('background-color', '#3a7d44');
                        }
                    });
                }
            },
            onLoadSuccess: function () {
                initializeRowListeners();
            }
        });
    }

    $(document).ready(function () {
        $('.tab-button').click(function () {
            $('.tab-button').removeClass('active');
            $(this).addClass('active');
            const schedule = $(this).data('tab');
            loadTableData(schedule);
        });

        // Load initial data for the first tab
        loadTableData('ProductionPlanBT');
    });

    saveChangesButton.addEventListener('click', function () {
        $('#editForm').submit();
    });
});


document.addEventListener('DOMContentLoaded', function() {
    const $table = $('#scheduleTable');
    const editModal = document.getElementById('uniqueEditModal');
    const editForm = document.getElementById('uniqueEditForm');
    const editModalTitle = document.getElementById('uniqueEditModalTitle');
    const csrfToken = getCookie('csrftoken'); // CSRF token for secure AJAX requests
    let currentScheduleId = null;
    let operators = [];
    let operatorMap = {}; // Map to hold username to full_name mapping
    let cncMachines = [];
    let cncMachineMap = {};

    // Fetch schedule data from the server
    function fetchSchedules() {
        fetch('/get-schedule/', {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest' // Indicates AJAX request
            }
        })
            .then(response => response.json())
            .then(data => {
                initTable(data);
            })
            .catch(error => console.error('Error fetching schedules:', error));
    }

    // Fetch operators from the server
    function fetchOperators() {
        fetch('/get-operators/', {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest' // Indicates AJAX request
            }
        })
            .then(response => response.json())
            .then(data => {
                operators = data.operators;
                // Populate the map with operator usernames and their corresponding full names
                operators.forEach(op => {
                    operatorMap[op.username] = op.full_name;
                });
                fetchCncMachines(); // Fetch CNC machines after operators are loaded
            })
            .catch(error => console.error('Error fetching operators:', error));
    }

    // Fetch CNC machines from the server
    function fetchCncMachines() {
        fetch('/get_cnc_machines/', {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest' // Indicates AJAX request
            }
        })
            .then(response => response.json())
            .then(data => {
                cncMachines = data;
                // Populate the map with CNC machine names and their corresponding IDs
                cncMachines.forEach(machine => {
                    cncMachineMap[machine.name] = machine.id;
                });
                fetchSchedules(); // Fetch schedules after CNC machines are loaded
            })
            .catch(error => console.error('Error fetching CNC machines:', error));
    }

    // Initialize the table with options
    function initTable(data) {
        $table.bootstrapTable('destroy').bootstrapTable({
            columns: [
                { field: 'id', title: 'ИД', sortable: true },
                { field: 'startDate', title: 'Дата начала', sortable: true},
                { field: 'endDate', title: 'Дата окончания', sortable: true},
                { field: 'productType', title: 'Тип продукта', sortable: true },
                { field: 'quantity', title: 'Колличество', sortable: true },
                { field: 'comments', title: 'Комментарий от OTK', sortable: true },
                { 
                    field: 'operatorName', 
                    title: 'Имя оператора',
                    formatter: function(value) {
                        const fullName = operatorMap[value] || value;
                        return `${value} - ${fullName}`;
                    },
                    sortable: true
                },
                { field: 'cncMachine.name', title: 'Станок с ЧПУ', sortable: true },
                { 
                    field: 'urgent', 
                    title: 'Срочно?', 
                    align: 'center',
                    formatter: function(value) {
                        return value ? '<span class="urgent-cell"><i class="fa fa-exclamation-circle" aria-hidden="true"></i> Да</span>' : '';
                    },
                    sortable: true
                },
                { field: 'completed', title: 'Завершено', align: 'center',
                    formatter: function(value) {
                        return value ? '<span class="completed"><i class="fa fa-check-circle" aria-hidden="true"></i> Да</span>' : '';
                    },
                    sortable: true },
                { field: 'startTime', title: 'Время начала', sortable: true, formatter: convertUTCToLocalFormatter },
                { field: 'endTime', title: 'Время окончания', sortable: true, formatter: convertUTCToLocalFormatter },
                { field: 'timeTaken', title: 'Затраченное время (м)', sortable: true, align: 'center',
                    formatter: function(value) {
                        if (value) {
                          // Add Font Awesome icon before the value
                          return '<span class="time"><i class="fa fa-clock" aria-hidden="true"></i> ' + value + ' Мин.</span>';
                        } else {
                          return ''; // Or return a default text like "No data" if needed
                        }
                      }
                    
                 },
                { field: 'planner_comment', title: 'Комментарий от оператора', sortable: true },
                { field: 'is_paused', title: 'График приостановлен', sortable: true , align: 'center',
                    formatter: function(value) {
                        return value ? '<span class="isPaused"><i class="fa fa-pause-circle" aria-hidden="true"></i> Да</span>' : '';
                    }
                },
                { field: 'last_paused_time', title: 'Время последней Приостановки', sortable: true, formatter: convertUTCToLocalFormatter },
                { field: 'details_quantity', title: 'Количество деталей', sortable: true },
                { field: 'details_time', title: 'Время на деталь', sortable: true },
                { 
                    field: 'actions', 
                    title: 'Действия', 
                    align: 'center',
                    formatter: function(value, row) {
                        return `
                        <div class="cncschedulebuttons">
                            <button class="btn btn-primary btn-sm btn-edit" data-id="${row.id}"><i class="fa fa-pencil" aria-hidden="true"></i></button>
                            <button class="btn btn-danger btn-sm ml-2 btn-delete" data-id="${row.id}"><i class="fa fa-trash" aria-hidden="true"></i></button>
                        </div>
                        `;
                    }
                }
            ],
            data: data,
            search: true,
            pagination: true,
            showRefresh: true,
            showColumns: true,
            clickToSelect: true,
            showExport: true,
            // exportTypes: ['csv', 'excel'],
            filterControl: true,
            showPaginationSwitch: true,
            pageList: [5, 10, 25, 50, 100, 'all'],
           
        });

        $table.on('click', '.btn-edit', function() {
            const scheduleId = $(this).data('id');
            const schedule = data.find(item => item.id === scheduleId);
            if (schedule) {
                openEditModal(schedule);
            } else {
                console.error('Schedule not found for ID:', scheduleId);
            }
        });

        $table.on('click', '.btn-delete', function() {
            const scheduleId = $(this).data('id');
            if (confirm('Вы уверены, что хотите удалить это График?')) {
                deleteSchedule(scheduleId);
            }
        });
    }
    // Formatter function to convert UTC time to local time
    function convertUTCToLocalFormatter(value) {
        if (!value) return '';
        const localTime = new Date(value);
        // return localTime.toLocaleString();  // Customize the format if needed
        return moment.utc(value).local().format('YYYY-MM-DD HH:mm:ss');  // Customize the format
    }

    function openEditModal(schedule) {
        currentScheduleId = schedule.id;
        if (editModalTitle) {
            editModalTitle.textContent = `Редактировать График: № ${schedule.id}`;
        } else {
            console.error('Edit modal title element not found.');
        }
    
        // Ensure form elements exist before setting values
        const startDateField = document.getElementById('uniqueEditStartDate');
        const endDateField = document.getElementById('uniqueEditEndDate');
        const productTypeField = document.getElementById('uniqueEditProductType');
        const quantityField = document.getElementById('uniqueEditQuantity');
        
        const orderNumField = document.getElementById('uniqueEditOrderNum');
        const limtzField = document.getElementById('uniqueEditLimtz');
        const commentNumField = document.getElementById('uniqueEditComment');

        const operatorNameField = document.getElementById('uniqueEditOperatorName');
        const cncMachineNameField = document.getElementById('uniqueEditCncMachineName');
        const urgentField = document.getElementById('uniqueEditUrgent');
        const filesField = document.getElementById('uniqueEditFiles');  // This is the file input field
        const uploadedFilesList = document.getElementById('uploadedFilesList');  // This is where we will display uploaded files
    
    
        if (startDateField && endDateField && productTypeField && quantityField && orderNumField && limtzField && commentNumField && operatorNameField && cncMachineNameField && urgentField) {
            startDateField.value = schedule.startDate;
            endDateField.value = schedule.endDate;
            productTypeField.value = schedule.productType;
            quantityField.value = schedule.quantity;

            orderNumField.value = schedule.orderNum;
            limtzField.value = schedule.limtz;
            commentNumField.value = schedule.comments;
    
            // Populate operator select field
            operatorNameField.innerHTML = operators.map(op => 
                `<option value="${op.username}" ${op.username === schedule.operatorName ? 'selected' : ''}>${op.username} - ${op.full_name}</option>`
            ).join('');
    
            // Populate CNC machine select field
            cncMachineNameField.innerHTML = cncMachines.map(machine => 
                `<option value="${machine.id}" ${machine.id === schedule.cncMachine.id ? 'selected' : ''}>${machine.name}</option>`
            ).join('');
    
            urgentField.checked = schedule.urgent === true; //'Yes';
            // Clear the list of uploaded files and populate it with the current schedule's files
            uploadedFilesList.innerHTML = '';
            if (schedule.files && schedule.files.length > 0) {
                schedule.files.forEach(file => {
                    uploadedFilesList.innerHTML += `
                        <div>
                            <a href="${file.url}" target="_blank">${file.name}</a>
                            <button type="button" data-file-id="${file.id}" class="btn btn-danger btn-sm ml-2 delete-file">Delete</button>
                        </div>
                    `;
                });
            } else {
                uploadedFilesList.innerHTML = '<p>По этому графику файлы не загружались</p>';
            }
        } else {
            console.error('One or more form elements are not found.');
        }
    
        $(editModal).modal('show'); // Show modal using Bootstrap
    }
    // Attach a single event listener to the parent element
    document.getElementById('uploadedFilesList').addEventListener('click', function(event) {
        if (event.target && event.target.matches('button.delete-file')) {
            const fileId = event.target.getAttribute('data-file-id');
            deleteFile(fileId);
        }
    });

    // Function to handle file deletion
    function deleteFile(fileId) {
        if (confirm('Вы уверены, что хотите удалить этот файл?')) {
            fetch(`/delete-file/${fileId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Remove the file from the list
                    document.getElementById(`file-${fileId}`).remove();
                    console.log('Файл успешно удален!');
                } else {
                    console.error('Error deleting file:', data.error);
                }
            })
            .catch(error => console.error('Error:', error));
        }
    }



    // Update schedule details
    function updateSchedule() {
        const formData = new FormData(editForm);
        const cncMachineName = formData.get('cncMachineName');
        const cncMachineId = cncMachineMap[cncMachineName];

        const updatedData = {
            id: currentScheduleId,
            startDate: formData.get('startDate'),
            endDate: formData.get('endDate'),
            productType: formData.get('productType'),
            quantity: formData.get('quantity'),
            orderNum: formData.get('orderNum'),
            operatorName: formData.get('operatorName'),
            cncMachineId: cncMachineName,
            urgent: formData.get('urgent') === 'on',
            limtz: formData.get('limtz'),
            comments: formData.get('comment')
        };

        console.log('Updated Data:', updatedData); // Debug output

        fetch('/update-schedule/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'  // Set this to identify AJAX requests
            },
            body: JSON.stringify(updatedData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Schedule updated successfully');

                // Now handle the file uploads (if any files were selected)
                const files = document.getElementById('uniqueEditFiles').files;
                if (files.length > 0) {
                    const fileData = new FormData();  // Create a FormData object to send the files
                    fileData.append('id', currentScheduleId);  // Include the schedule ID

                    for (let i = 0; i < files.length; i++) {
                        fileData.append('files', files[i]);  // Append each file
                    }

                    fetch('/upload-files/', {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrfToken,  // Ensure CSRF token is included
                            'Accept': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest' // Indicates AJAX request
                        },
                        body: fileData  // Send the files
                    })
                    .then(response => response.json())
                    .then(fileResponse => {
                        if (fileResponse.success) {
                            console.log('Files uploaded successfully');
                        } else {
                            console.error('Error uploading files:', fileResponse.error);
                        }
                    })
                    .catch(fileError => console.error('Error uploading files:', fileError));
                }

                
                $(editModal).modal('hide'); // Hide modal using Bootstrap
                fetchSchedules(); // Refresh table
            } else {
                console.error('Error updating schedule:', data.error);
            }
        })
        .catch(error => console.error('Error:', error));
    }

    // Function to delete a schedule
    function deleteSchedule(id) {
        fetch(`/delete-schedule-table/${id}/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {
            if (response.ok) {
                fetchSchedules(); // Refresh table after deletion
            } else {
                console.error('Failed to delete schedule');
            }
        })
        .catch(error => console.error('Error deleting schedule:', error));
    }

    // Function to get CSRF token for AJAX requests
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Handle form submission to update schedule
    editForm.addEventListener('submit', function(e) {
        e.preventDefault();
        updateSchedule();
    });

    // Initial load
    fetchOperators(); // Fetch operators first
});
