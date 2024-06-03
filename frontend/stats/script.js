function getUserId() {
    let id = localStorage.getItem(CACHE_USER_ID_KEY);
    return id ? Number(id) : null;
}

function getUserName() {
    return localStorage.getItem(CACHE_USER_NAME_KEY);
}

CACHE_USER_ID_KEY = 'user_id';
CACHE_USER_NAME_KEY = 'user_name';

document.addEventListener("DOMContentLoaded", function() {
    let user_name = getUserName();
    $("#username").text(user_name);

    // Logout button functionality
    document.getElementById('logoutBtn').addEventListener('click', function() {
        localStorage.removeItem('user_id');
        localStorage.removeItem('user_name');
        window.location.href = '/';
    });

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

// Check if user is logged in
const user_id = localStorage.getItem('user_id');

// Verify user function
function verifyUser() {
    const user_id = localStorage.getItem('user_id');
    const user_name = localStorage.getItem('user_name');

    if (!user_id || !user_name) {
        return Promise.resolve(false);
    }

    return fetch(`/verify_user?user_id=${user_id}&user_name=${user_name}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(response => {
        if (response.status === 404) {
           handleUnauthorizedUser()
        }
        return response.json();
    })
    .then(data => {
       return data.is_admin
    })
    .catch(error => {
        console.error("An error occurred while verifying the user:", error);
        return false;
    });
}

function handleUnauthorizedUser() {
    alert('Invalid User!!');
    localStorage.removeItem(CACHE_USER_ID_KEY);
    localStorage.removeItem(CACHE_USER_NAME_KEY);
    window.location.href = '/';
}
verifyUser().then(isVerified => {
    if (!isVerified) {
        alert('Invalid User!!');
        localStorage.removeItem('user_id');
        localStorage.removeItem('user_name');
        window.location.href = '/';
    }
});