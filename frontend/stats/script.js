document.addEventListener("DOMContentLoaded", function() {
    fetch('/metrics/user_event_counts')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('userEventChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.map(item => item.event_name),
                    datasets: [{
                        label: '# of Events',
                        data: data.map(item => item.event_count),
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error fetching user event counts:', error));

    fetch('/metrics/most_liked_tracks')
        .then(response => response.json())
        .then(data => {
            const mostLikedTracksList = document.getElementById('mostLikedTracks');
            data.forEach(track => {
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item';
                listItem.textContent = `${track.track_id}: ${track.like_count} likes`;
                mostLikedTracksList.appendChild(listItem);
            });
        })
        .catch(error => console.error('Error fetching most liked tracks:', error));

    fetch('/metrics/user_activity')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('userActivityChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.map(item => `User ${item.user_id}`),
                    datasets: [{
                        label: 'User Activity',
                        data: data.map(item => item.activity_count),
                        backgroundColor: 'rgba(153, 102, 255, 0.2)',
                        borderColor: 'rgba(153, 102, 255, 1)',
                        borderWidth: 1,
                        fill: true
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error fetching user activity:', error));
});
