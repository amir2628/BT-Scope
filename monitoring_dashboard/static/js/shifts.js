document.addEventListener('DOMContentLoaded', function () {
    // Initialize variables and elements
    const todayButton = document.getElementById('today');
    const prevMonthButton = document.getElementById('prevMonth');
    const nextMonthButton = document.getElementById('nextMonth');
    const monthYearElem = document.getElementById('monthYear');
    const daysHeader = document.getElementById('days-header');
    const shiftsHeader = document.getElementById('shifts-header');
    const scheduleBody = document.getElementById('schedule-body');
    const shiftForm = document.getElementById('shiftForm');
    const shiftStartInput = document.getElementById('shiftStart');
    const shiftEndInput = document.getElementById('shiftEnd');
    const notesInput = document.getElementById('notes');
    const deleteButton = document.querySelector('.btn.delete');
  
    let currentMonth = new Date().getMonth();
    let currentYear = new Date().getFullYear();
    let activeCell = null;
    let activeShift = null;
  
    // Initialize date picker
    $('#monthYear').datepicker({
      format: 'mm/yyyy',
      startView: 1,
      minViewMode: 1,
      autoclose: true,
      todayHighlight: true,
      language: 'ru' // Set language to Russian
    }).on('changeDate', function (e) {
      const selectedMonth = e.date.getMonth();
      const selectedYear = e.date.getFullYear();
      currentMonth = selectedMonth;
      currentYear = selectedYear;
      renderCalendar(currentMonth, currentYear);
    });
  
    // Function to get a cookie by name
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
  
    // Function to adjust cell sizes
    function adjustCellSizes() {
      const cells = document.querySelectorAll('#schedule-body td');
      const columnWidths = Array.from(cells).reduce((widths, cell) => {
        const colIndex = cell.cellIndex;
        const contentWidth = cell.scrollWidth;
  
        if (!widths[colIndex] || contentWidth > widths[colIndex]) {
          widths[colIndex] = contentWidth;
        }
  
        return widths;
      }, []);
  
      cells.forEach(cell => {
        cell.style.width = columnWidths[cell.cellIndex] + 'px';
      });
  
      const rows = document.querySelectorAll('#schedule-body tr');
      rows.forEach(row => {
        const maxHeight = Array.from(row.cells).reduce((max, cell) => {
          return Math.max(max, cell.scrollHeight);
        }, 0);
        row.style.height = maxHeight + 'px';
      });
    }
  
    // Function to fetch and display shifts including overtime
    async function fetchAndDisplayShifts(firstDay, lastDate) {
      try {
        const response = await fetch(`/api/shifts/${currentYear}/${currentMonth + 1}/`);
        const shifts = await response.json();
  
        const rows = document.querySelectorAll('#schedule-body tr');
  
        shifts.forEach(shift => {
          const shiftDate = new Date(shift.date);
          const day = shiftDate.getDate();
          const row = Array.from(rows).find(row => row.getAttribute('data-user-id') === String(shift.user_id));
          if (row) {
            const cell = row.querySelector(`td[data-date="${day}"]`);
            if (cell) {
              cell.innerHTML = `<div class="shift" style="background-color: ${getRandomColor()};">
                ${shift.start_time} - ${shift.end_time}<br>
                ${shift.notes}<br>
                ${shift.overtime_start_time && shift.overtime_end_time ? `Переработка: ${shift.overtime_start_time} - ${shift.overtime_end_time}` : ''}
              </div>`;
            }
          }
        });
  
        rows.forEach(row => calculateTotalHours(row));
  
      } catch (error) {
        console.error('Ошибка при получении смен:', error);
      }
    }
  
    function renderCalendar(month, year) {
      const firstDay = new Date(year, month, 1).getDay();
      const lastDate = new Date(year, month + 1, 0).getDate();
      const today = new Date();
  
      daysHeader.innerHTML = '';
      shiftsHeader.innerHTML = '';
      scheduleBody.innerHTML = '';
  
      let daysHtml = [];
      let shiftsHtml = [];
  
      let currentDayCell = null;
  
      daysHtml.push('<th></th>');
      shiftsHtml.push('<th></th>');
  
      for (let day = 1; day <= lastDate; day++) {
        const date = new Date(year, month, day);
        const dayName = date.toLocaleDateString('ru-RU', { weekday: 'long' });
        const isToday = today.getFullYear() === year && today.getMonth() === month && today.getDate() === day;
        const dayClass = isToday ? 'current-day' : '';
  

        // If today, add the calendar icon before the day name
        const iconHtml = isToday ? '<i class="fa fa-calendar-check" aria-hidden="true"></i> ' : '';

        daysHtml.push(`<th colspan="2" class="${dayClass}">${iconHtml} ${dayName}, ${day}</th>`);
        
        // daysHtml.push(`<th colspan="2" class="${dayClass}">${dayName}, ${day}</th>`);
        shiftsHtml.push('<th><i class="fa fa-sun" aria-hidden="true"></i> Дневная смена</th><th><i class="fa fa-moon" aria-hidden="true"></i> Ночная смена</th>');
  
        if (isToday) {
          currentDayCell = day;
        }
      }
  
      daysHtml.push('<th>Итоговые часы</th>');
      shiftsHtml.push('<th></th>');
  
      daysHeader.innerHTML = `<tr>${daysHtml.join('')}</tr>`;
      shiftsHeader.innerHTML = `<tr>${shiftsHtml.join('')}</tr>`;
  
      fetchEmployeeRows(firstDay, lastDate).then(employeeRowsHtml => {
        scheduleBody.innerHTML = employeeRowsHtml;
        monthYearElem.innerText = `${getMonthName(month)} ${year}`;
  
        fetchAndDisplayShifts(firstDay, lastDate);  // Fetch and display shifts
  
        adjustCellSizes();
  
        if (currentDayCell !== null) {
          scrollToDay(currentDayCell);
        }
      });
    }
  
    // Function to scroll to a specific day
    function scrollToDay(day) {
      const cells = document.querySelectorAll('#schedule-body td');
      const totalDays = cells.length / document.querySelectorAll('#schedule-body tr')[0].cells.length;
  
      const rowIndex = Math.floor((day - 1) * 2 / totalDays);
      const cellIndex = ((day - 1) * 2) % totalDays;
  
      const targetCell = cells[rowIndex * totalDays + cellIndex];
  
      if (targetCell) {
        targetCell.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });
      }
    }
  
    // Function to get month name
    function getMonthName(month) {
      return ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'][month];
    }
  
    // Function to change month
    function changeMonth(delta) {
      currentMonth += delta;
      if (currentMonth > 11) {
        currentMonth = 0;
        currentYear++;
      } else if (currentMonth < 0) {
        currentMonth = 11;
        currentYear--;
      }
      renderCalendar(currentMonth, currentYear);
    }
  
    // Function to fetch employee rows
    async function fetchEmployeeRows(firstDay, lastDate) {
      const response = await fetch('/api/employees/');
      const employees = await response.json();
      const totalDays = lastDate;
      console.log("here are the employees: ", employees)
      // <div class="employee-info">${emp.name}<br><span>${emp.role}</span></div>
      return employees.filter(emp => emp.role === '(regular_user)' || emp.role === '(operator)').map(emp => `
        <tr data-user-id="${emp.id}">
          <td>
            <div class="employee">
              <div class="employee-info">${emp.name}</div>
            </div>
          </td>
          ${Array.from({ length: totalDays }).map((_, i) => `
            <td ondblclick="openForm(this)" data-date="${i + 1}"></td>
            <td ondblclick="openForm(this)" data-date="${i + 1}"></td>
          `).join('')}
          <td class="total-hours">0</td>
        </tr>
      `).join('');
    }

    // Function to generate a random color from a predefined set of hex color codes
    function getRandomColor() {
        // Define an array of hex color codes
        const colorSet = [
        '#e9c46a', // Example colors
        '#f4a261',
        '#e76f51',
        '#2a9d8f',
        '#bc6c25',
        '#669bbc',
        '#f77f00',
        '#eae2b7',
        '#9e2a2b',
        '#ffd166',
        '#90a955',
        '#4f772d',
        
        // Add as many colors as you need
        ];
    
        // Select a random color from the array
        const randomColor = colorSet[Math.floor(Math.random() * colorSet.length)];
    
        return randomColor;
    }
    
  
    // Function to open the shift form
    window.openForm = function (cell) {
      activeCell = cell;
      activeShift = cell.querySelector('.shift');
      shiftForm.style.display = 'block';
      const rect = cell.getBoundingClientRect();
      shiftForm.style.top = rect.top + window.scrollY + 'px';
      shiftForm.style.left = rect.left + window.scrollX + 'px';
  
      if (activeShift) {
        const [time, notes] = activeShift.innerHTML.split('<br>');
        const [startTime, endTime] = time.split(' - ');
        shiftStartInput.value = startTime.trim();
        shiftEndInput.value = endTime.trim();
        notesInput.value = notes.trim();
        deleteButton.style.display = 'inline-block';
      } else {
        shiftStartInput.value = '';
        shiftEndInput.value = '';
        notesInput.value = '';
        deleteButton.style.display = 'none';
      }
    };
  
    // Function to close the shift form
    window.closeForm = function () {
      shiftForm.style.display = 'none';
    };
  
  // Function to calculate total hours
  function calculateTotalHours(row) {
    const cells = row.querySelectorAll('td');
    let totalShiftSeconds = 0;
    let totalOvertimeSeconds = 0;
  
    cells.forEach(cell => {
      const shiftElement = cell.querySelector('.shift');
      if (shiftElement) {
        const shiftContent = shiftElement.innerHTML;
        const parts = shiftContent.split('<br>').map(part => part.trim());
  
        if (parts.length > 0) {
          // Regular shift times
          const time = parts[0];
          const shiftDetails = time.split(' - ');
          if (shiftDetails.length === 2) {
            const startTime = shiftDetails[0].trim();
            const endTime = shiftDetails[1].trim();
  
            // Calculate regular shift duration
            const start = new Date(`1970-01-01T${startTime}Z`);
            const end = new Date(`1970-01-01T${endTime}Z`);
            const durationInSeconds = (end - start) / 1000; // Convert milliseconds to seconds
            totalShiftSeconds += durationInSeconds;
          }
        }
  
        if (parts.length > 1) {
          // Overtime notes
          const notes = parts.slice(1).join(' '); // Join remaining parts to handle cases where there are multiple <br> tags
          console.log('Notes:', notes); // Debugging: Output notes to check format
  
          const overtimeMatches = notes.match(/(\d{2}:\d{2}:\d{2})\s*-\s*(\d{2}:\d{2}:\d{2})/);
          if (overtimeMatches) {
            const overtimeStartTime = overtimeMatches[1];
            const overtimeEndTime = overtimeMatches[2];
            console.log('Overtime Start Time:', overtimeStartTime); // Debugging: Output start time
            console.log('Overtime End Time:', overtimeEndTime); // Debugging: Output end time
  
            const overtimeStart = new Date(`1970-01-01T${overtimeStartTime}Z`);
            const overtimeEnd = new Date(`1970-01-01T${overtimeEndTime}Z`);
            const overtimeDurationInSeconds = (overtimeEnd - overtimeStart) / 1000; // Convert milliseconds to seconds
            totalOvertimeSeconds += overtimeDurationInSeconds;
            console.log('Overtime Duration (seconds):', overtimeDurationInSeconds); // Debugging: Output duration
          } else {
            console.log('No overtime match found in notes'); // Debugging: Output if no match is found
          }
        }
      }
    });
  
    const shiftHours = Math.floor(totalShiftSeconds / 3600);
    const shiftMinutes = Math.floor((totalShiftSeconds % 3600) / 60);
    const shiftSeconds = Math.floor(totalShiftSeconds % 60);
  
    const overtimeHours = Math.floor(totalOvertimeSeconds / 3600);
    const overtimeMinutes = Math.floor((totalOvertimeSeconds % 3600) / 60);
    const overtimeSeconds = Math.floor(totalOvertimeSeconds % 60);
  
    const totalHoursCell = row.querySelector('.total-hours');
    totalHoursCell.textContent = `Смены: ${shiftHours} час(а), ${shiftMinutes} минут(а), ${shiftSeconds} секунд | Переработка: ${overtimeHours} час(а), ${overtimeMinutes} минут(а), ${overtimeSeconds} секунд`;
  }
  
  
  
    // Function to convert 12-hour time format to 24-hour time format
    function convertTo24Hour(time12h) {
      const [time, modifier] = time12h.split(' ');
      let [hours, minutes] = time.split(':');
      if (modifier === 'PM' && hours !== '12') {
          hours = parseInt(hours, 10) + 12;
      }
      if (modifier === 'AM' && hours === '12') {
          hours = '00';
      }
      return `${String(hours).padStart(2, '0')}:${minutes}`;
    }
  
    // Function to save shift including overtime times
    window.saveShift = function () {
      if (activeCell) {
        let startTime = shiftStartInput.value;
        let endTime = shiftEndInput.value;
        const notes = notesInput.value;
        let overtimeStart = document.getElementById('overtimeStart').value;
        let overtimeEnd = document.getElementById('overtimeEnd').value;
  
        if (startTime && endTime) {
          // Convert start and end times to 24-hour format
          startTime = convertTo24Hour(startTime);
          endTime = convertTo24Hour(endTime);
          overtimeStart = convertTo24Hour(overtimeStart);
          overtimeEnd = convertTo24Hour(overtimeEnd);
  
          const colorClass = activeShift ? activeShift.className.split(' ').pop() : getRandomColor();
          activeCell.innerHTML = `<div class="shift" style="background-color: ${colorClass};">
            ${startTime} - ${endTime}<br>${notes}
            ${overtimeStart && overtimeEnd ? `<br>Переработка: ${overtimeStart} - ${overtimeEnd}` : ''}
          </div>`;
  
          const row = activeCell.closest('tr');
          const userId = row.getAttribute('data-user-id');
          const day = activeCell.getAttribute('data-date');
  
          const fullDate = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
  
          const shiftType = activeCell.cellIndex % 2 === 0 ? 'day' : 'night';
          
          fetch('/api/save_shift/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
              user_id: userId,
              shift_type: shiftType,
              date: fullDate,
              start_time: startTime,
              end_time: endTime,
              overtime_start_time: overtimeStart,
              overtime_end_time: overtimeEnd,
              notes: notes
            })
          })
          .then(response => response.json())
          .then(data => {
            if (data.success) {
              calculateTotalHours(row);
            } else {
              console.error(data.message);
            }
          })
          .catch(error => {
            console.error('Ошибка при сохранении смены:', error);
          })
          .finally(() => {
            closeForm();
          });
        } else {
          activeCell.innerHTML = '';
          closeForm();
        }
      }
    };
  
    // Function to delete a shift
    window.deleteShift = function () {
      if (activeCell && activeShift) {
        activeCell.innerHTML = '';
        activeShift = null;
  
        const row = activeCell.closest('tr');
        calculateTotalHours(row);
  
        closeForm();
      }
    };
  
    // Event listeners for navigation buttons
    todayButton.addEventListener('click', function () {
      const today = new Date();
      currentMonth = today.getMonth();
      currentYear = today.getFullYear();
      renderCalendar(currentMonth, currentYear);
    });
    
    prevMonthButton.addEventListener('click', function () {
      changeMonth(-1);
    });
  
    nextMonthButton.addEventListener('click', function () {
      changeMonth(1);
    });
  
    // Initial render of the calendar
    renderCalendar(currentMonth, currentYear);
  
    // Initialize flatpickr for time inputs
    flatpickr('.time-picker', {
      enableTime: true,
      noCalendar: true,
      dateFormat: "h:i K",
    });
  });
  
  