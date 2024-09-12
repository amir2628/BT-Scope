// monitoring_dashboard/static/js/main.js

document.addEventListener("DOMContentLoaded", function() {
    // Add any JavaScript for animations here

    // Example: Fade-in effect for content
    const content = document.querySelector('.content');
    content.style.opacity = 0;
    content.style.transition = 'opacity 2s';
    setTimeout(() => {
        content.style.opacity = 1;
    }, 100);

    // Example: Smooth scrolling for sidebar links
    const sidebarLinks = document.querySelectorAll('.sidebar ul li');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function() {
            sidebarLinks.forEach(link => link.classList.remove('active'));
            this.classList.add('active');
            // You can add smooth scrolling logic here if needed
        });
    });

    const monthSelect = document.getElementById("monthSelect");
    const yearSelect = document.getElementById("yearSelect");
    const todayButton = document.getElementById("todayButton");
    const editScheduleButton = document.getElementById("editScheduleButton");
    const calendarBody = document.querySelector("#calendar tbody");
    const modal = document.getElementById("modal");
    const closeButton = document.querySelector(".close");
    const scheduleForm = document.getElementById("scheduleForm");

    const eventColors = {
        work: "work",
        holiday: "holiday",
        meeting: "meeting",
    };

    const events = {};


    const tooltip = document.getElementById('tooltip');

    function generateCalendar(month, year) {
        calendarBody.innerHTML = "";
        const firstDay = new Date(year, month).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();

        let date = 1;

        for (let i = 0; i < 6; i++) {
            const row = document.createElement("tr");

            for (let j = 0; j < 7; j++) {
                const cell = document.createElement("td");

                if (i === 0 && j < firstDay) {
                    cell.appendChild(document.createTextNode(""));
                } else if (date > daysInMonth) {
                    break;
                } else {
                    cell.appendChild(document.createTextNode(date));

                    const eventKey = `${year}-${month + 1}-${date}`;
                    if (events[eventKey]) {
                        const eventDiv = document.createElement("div");
                        eventDiv.className = `event ${eventColors[events[eventKey].event]}`;
                        eventDiv.textContent = events[eventKey].productType;
                        cell.appendChild(eventDiv);
                    }

                    cell.addEventListener('mouseenter', function() {
                        if (events[eventKey]) {
                            tooltip.innerHTML = `
                                <strong>${events[eventKey].productType}</strong><br>
                                Quantity: ${events[eventKey].quantity}<br>
                                Operator: ${events[eventKey].operatorName}<br>
                                Machine: ${events[eventKey].cncMachine}
                            `;
                            tooltip.style.display = 'block';
                            tooltip.style.left = `${event.pageX + 10}px`;
                            tooltip.style.top = `${event.pageY + 10}px`;
                        }
                        cell.style.backgroundColor = '#41737a';
                    });

                    cell.addEventListener('mouseleave', function() {
                        tooltip.style.display = 'none';
                        if (events[eventKey]) {
                            const eventClass = eventColors[events[eventKey].event];
                            cell.style.backgroundColor = eventClass === 'work' ? '#1e536e' : (eventClass === 'holiday' ? '#f0ad4e' : '#d9534f');
                        } else {
                            cell.style.backgroundColor = '#243c44';
                        }
                    });

                    cell.addEventListener('mousemove', function(event) {
                        tooltip.style.left = `${event.pageX + 10}px`;
                        tooltip.style.top = `${event.pageY + 10}px`;
                    });

                    date++;
                }

                row.appendChild(cell);
            }

            calendarBody.appendChild(row);
        }
    }

    

    function populateSelectElements() {
        const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
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
        generateCalendar(now.getMonth(), now.getFullYear());
    }

    function showModal() {
        modal.style.display = "block";
    }

    function closeModal() {
        modal.style.display = "none";
    }

    function addEvent(e) {
        e.preventDefault();
        const formData = new FormData(scheduleForm);
        const date = formData.get("date");

        events[date] = {
            event: "work",
            productType: formData.get("productType"),
            quantity: formData.get("quantity"),
            operatorName: formData.get("operatorName"),
            cncMachine: formData.get("cncMachine"),
        };

        const [year, month] = date.split("-").map(Number);
        generateCalendar(month - 1, year);
        closeModal();
    }

    todayButton.addEventListener("click", showToday);
    editScheduleButton.addEventListener("click", showModal);
    closeButton.addEventListener("click", closeModal);
    window.addEventListener("click", function (event) {
        if (event.target == modal) {
            closeModal();
        }
    });

    scheduleForm.addEventListener("submit", addEvent);

    populateSelectElements();
    generateCalendar(monthSelect.value, yearSelect.value);

    monthSelect.addEventListener("change", () => generateCalendar(monthSelect.value, yearSelect.value));
    yearSelect.addEventListener("change", () => generateCalendar(monthSelect.value, yearSelect.value));


    function addEvent(e) {
        e.preventDefault();
        const formData = new FormData(scheduleForm);
    
        // Send form data to Django backend
        fetch('/add-schedule/', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json()) // Parse response as JSON
        .then(data => {
            if (data.success) {
                // Schedule added successfully, close modal and update calendar
                closeModal();
                const date = formData.get("date");
                const [year, month] = date.split("-").map(Number);
                generateCalendar(month - 1, year);
            } else {
                // Error occurred, handle accordingly
                console.error('Failed to add schedule:', data.error);
            }
        })
        .catch(error => {
            console.error('Error adding schedule:', error);
        });
    }

    // Fetch schedule details from Django backend
    fetch('/get-schedule/')
    .then(response => response.json())
    .then(data => {
        data.forEach(schedule => {
            const scheduleDate = new Date(schedule.date);
            const eventKey = `${scheduleDate.getFullYear()}-${scheduleDate.getMonth() + 1}-${scheduleDate.getDate()}`;
            events[eventKey] = {
                event: "work",
                productType: schedule.product_type,
                quantity: schedule.quantity,
                operatorName: schedule.operator_name,
                cncMachine: schedule.cnc_machine,
            };
        });
        generateCalendar(monthSelect.value, yearSelect.value);
    })
    .catch(error => console.error('Error fetching schedule:', error));

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
            labels: ['Active', 'Inactive'],
            datasets: [{
                label: 'Machines Active',
                data: [70, 30],
                backgroundColor: ['#ffb703', '#ff9742'],
                borderColor: ['#3498db', '#e74c3c'],
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
