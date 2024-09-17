// fetching data from the MariaDB and populate the charts in inventory

document.addEventListener('DOMContentLoaded', function() {
    // Fetch and render Total Materials Chart
    fetch('/get-materials-chart-data/', {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest' // Indicates AJAX request
        }
    })
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('TotalMaterialsChart').getContext('2d');
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.data,
                        backgroundColor: ['#2ecc71', '#f1c40f', '#FF6666']
                    }]
                },
                options: {
                    plugins: {
                        legend: {
                            display: true
                        }
                    }
                }
            });
        });

    // Fetch and render Total Inventory Chart
    fetch('/get-inventory-chart-data/', {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest' // Indicates AJAX request
        }
    })
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('TotalInventoryChart').getContext('2d');
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.data,
                        backgroundColor: ['#2ecc71', '#f1c40f', '#FF6666']
                    }]
                },
                options: {
                    plugins: {
                        legend: {
                            display: true
                        }
                    }
                }
            });
        });

    // Fetch and render Deliveries Chart
    fetch('/get-deliveries-chart-data/', {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest' // Indicates AJAX request
        }
    })
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('deliveriesChart').getContext('2d');
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.data,
                        // backgroundColor: ['#2ecc71', '#e74c3c']
                        backgroundColor: ['#2ecc71', '#f1c40f', '#FF6666']
                    }]
                },
                options: {
                    plugins: {
                        legend: {
                            display: true
                        }
                    }
                }
            });
        });

    // Rest of your code remains unchanged
    // ...
});

