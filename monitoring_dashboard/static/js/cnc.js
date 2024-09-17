//  // CNC circle progress bar:

document.addEventListener("DOMContentLoaded", () => {
    // Set circle progress
    document.querySelectorAll('.circle').forEach(circle => {
        const percent = circle.getAttribute('data-percent');
        circle.style.setProperty('--percent', percent);
    });

    // Modal functionality
    const modal = document.getElementById("cutommodal");
    const span = document.getElementsByClassName("close")[0];

    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('click', () => {
            const id = card.getAttribute('data-id');
            showModal(id);
        });
    });

    span.onclick = function() {
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
    
    // Close modal functionality
    document.querySelector('.close').addEventListener('click', () => {
        document.getElementById('cutommodal').style.display = 'none';
    });
    
});


// ========> For notifications <=========
document.addEventListener('DOMContentLoaded', function() {
    const notificationContainer = document.querySelector('.notification-container');
    const notificationDropdown = document.querySelector('.notification-dropdown');
    const notificationList = document.querySelector('.notifications-list');
    const notificationCount = document.querySelector('.notification-count');
    const bellIcon = document.querySelector('.notification-container .fa-bell');
    let notifications = [];

    // Fetch notifications
    function fetchNotifications() {
        fetch('/get-notifications/', {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest' // Indicates AJAX request
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    notifications = data.notifications;
                    renderNotifications();
                    updateNotificationCount(data.unreadCount);
                }
            })
            .catch(error => console.error('Error fetching notifications:', error));
    }

    // Render notifications
    function renderNotifications() {
        notificationList.innerHTML = '';
        notifications.forEach(notification => {
            const notificationElement = document.createElement('div');
            notificationElement.classList.add('notification');
            if (notification.urgent) {
                notificationElement.classList.add('urgent');
            }
            notificationElement.innerHTML = `
                <h4>${notification.urgent ? 'СРОЧНО: ' : ''}${notification.schedule.productType}</h4>
                <p>${notification.message}</p>
            `;
            notificationList.appendChild(notificationElement);
        });
    }

    // Update notification count
    function updateNotificationCount(count) {
        notificationCount.textContent = count;
        if (count > 0) {
            notificationCount.style.display = 'inline-block';
            bellIcon.classList.add('has-notifications');
        } else {
            notificationCount.style.display = 'none';
            bellIcon.classList.remove('has-notifications');
        }
    }

    // Mark notifications as read
    function markNotificationsAsRead() {
        fetch('/mark-notifications-read/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'), // Ensure you include the CSRF token for security
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ user_id: userId }) // Use the userId variable defined in the template
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateNotificationCount(0);
                bellIcon.classList.remove('has-notifications');
            }
        })
        .catch(error => console.error('Error marking notifications as read:', error));
    }

    // Toggle notification dropdown
    notificationContainer.addEventListener('click', () => {
        const isDropdownVisible = notificationDropdown.classList.contains('open');
        notificationDropdown.classList.toggle('open', !isDropdownVisible);
        if (!isDropdownVisible) {
            markNotificationsAsRead();
        }
    });

    // Close notification dropdown when clicking outside
    document.addEventListener('click', (event) => {
        if (!notificationContainer.contains(event.target)) {
            notificationDropdown.classList.remove('open');
        }
    });

    // Prevent closing dropdown when clicking inside
    notificationDropdown.addEventListener('click', (event) => {
        event.stopPropagation();
    });

    // Fetch notifications on page load
    fetchNotifications();
});

// Utility function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
