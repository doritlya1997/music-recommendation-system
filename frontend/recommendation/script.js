CACHE_USER_ID_KEY = 'user_id';
CACHE_USER_NAME_KEY = 'user_name';
recommendation_list_size = 0;
user_like_or_dis_clicks_count = 0

function getUserId() {
    let id = localStorage.getItem(CACHE_USER_ID_KEY);
    return id ? Number(id) : null;
}

function getUserName() {
    return localStorage.getItem(CACHE_USER_NAME_KEY);
}

function processCSVData(csvData) {
    document.getElementById('loader-overlay').classList.remove('hidden'); // Show loader overlay

    let dataLines = csvData.split(/\r\n|\n/);
    if (dataLines.length <= 1) {
        alert('The CSV file is empty or improperly formatted.');
        document.getElementById('loader-overlay').classList.add('hidden'); // Hide loader overlay
        return;
    }
    let headers = dataLines[0].split(',');
    let rows = dataLines.slice(1);

    let track_id_list = [];
    let error_occurred = null;
    rows.forEach(row => {
        if (!error_occurred) {
            let columns = row.split(',');
            if (columns.length === headers.length) {
                track_id_list.push(extractTrackId(columns[0]));
            } else {
                alert('CSV Row does not match header length: ' + row);
                error_occurred = true;
            }
        }
    });

    if (!error_occurred) {
        fetch('/like/csv', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: getUserId(),
                user_name: getUserName(),
                track_ids: track_id_list,
                is_add_by_user: true
            })
        })
        .then(response => {
            if (response.status === 404) {
                handleUnauthorizedUser();
            }
            return response.json();
        })
        .then(data => {
            if (data.affected_rows > 0) {
                alert(data.affected_rows + " " + data.message);
                console.log('Songs liked:', data);
                refreshLikedSongs();
                refreshRecommendedSongs();
            } else {
                alert(data.message);
            }
            document.getElementById('loader-overlay').classList.add('hidden'); // Hide loader overlay
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('loader-overlay').classList.add('hidden'); // Hide loader overlay
        });

        document.getElementById('songInput').value = ''; // Clear input field
    } else {
        document.getElementById('loader-overlay').classList.add('hidden'); // Hide loader overlay
    }
}

function addSong() {
    let song_input = document.getElementById('songInput').value.trim();
    if (!song_input) {
        alert('Please enter a Spotify song link or upload a CSV file.');
        return;
    }

    let track_id = extractTrackId(song_input);
    if (track_id) {
        fetch('/like', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: getUserId(),
                user_name: getUserName(),
                track_id: track_id,
                is_add_by_user: true
            })
        })
        .then(response => {
            if (response.status === 404) {
                handleUnauthorizedUser();
            }
            return response.json();
        })
        .then(data => {
            if (data.affected_rows > 0) {
                alert(data.affected_rows + " " + data.message);
                console.log('Song liked:', data);
                refreshLikedSongs();
                refreshRecommendedSongs();
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });

        document.getElementById('songInput').value = '';
    } else {
        alert('This is not a Spotify song link.');
    }
}

function generateSongHTML({ track_id, track_name, artist_name, year, relevance_percentage, recommendation_type }, actions) {
    let percentage_element = relevance_percentage ? `<span class="percentage">${relevance_percentage}%</span>` : '';
    let link = 'https://open.spotify.com/track/' + track_id;
    let source_element = ""

    if (recommendation_type) {
        dict = {
            "user_history": { icon: "gg-girl", desc: "User Similarity" },
            "similar_users": { icon: "gg-music", desc: "Track Similarity" },
        }

        source_element = `<span class='track-source'>
                            <i class='${dict[recommendation_type].icon}'></i>
                            <span class="tooltip">${dict[recommendation_type].desc}</span>
                        </span>`
    }
    return `
        <div class="list-group-item">
            <div class="item-details">
                <span class="track-id hidden">${track_id}</span>
                <span class="track-source-text hidden">${recommendation_type}</span>
                <div class="track-name-container">
                    <span class="track-name">${track_name}</span>
                    ${percentage_element}
                </div>
                <div class="track-name-container">
                    <span class="artist-name">${artist_name}</span>
                    ${source_element}
                </div>
                <span class="year">(${year})</span>
                <a href="${link}" target="_blank" class="listen-link">Listen on Spotify</a>
            </div>
            <div class="button-group">
                ${actions}
            </div>
        </div>
    `;
}

function appendSongToLiked(songDetails) {
    let likedSongsList = document.getElementById('likedSongsList');
    let actions = `<button class="btn btn-danger" onclick="removeSongFromList(this, 'like')"><i class="fa fa-trash"></i> Remove</button>`;
    likedSongsList.innerHTML = generateSongHTML(songDetails, actions) + likedSongsList.innerHTML;
}

function appendSongToDisliked(songDetails) {
    let dislikedSongsList = document.getElementById('dislikedSongsList');
    let actions = `<button class="btn btn-danger" onclick="removeSongFromList(this, 'dislike')"><i class="fa fa-trash"></i> Remove</button>`;
    dislikedSongsList.innerHTML = generateSongHTML(songDetails, actions) + dislikedSongsList.innerHTML;
}

function appendSongToRecommendations(songDetails) {
    let recommendedSongsList = document.getElementById('recommendedSongsList');
    let actions = `
        <button class="btn btn-success" onclick="likeSong(this)"><i class="fa fa-thumbs-up"></i> Like</button>
        <button class="btn btn-danger" onclick="dislikeSong(this)"><i class="fa fa-thumbs-down"></i> Dislike</button>
    `;
    recommendedSongsList.innerHTML += generateSongHTML(songDetails, actions);
}

function extractTrackId(link) {
    const match = link.match(/track\/([a-zA-Z0-9]+)/);
    return match ? match[1] : null;
}

function likeSong(button) {
    let songItem = button.parentNode.parentNode;
    let songDetails = {
        track_id: songItem.querySelector('.track-id').textContent,
        track_name: songItem.querySelector('.track-name').textContent,
        artist_name: songItem.querySelector('.artist-name').textContent,
        year: songItem.querySelector('.year').textContent.replace('(', '').replace(')', '')
    };
    appendSongToLiked(songDetails);
    songItem.remove();

    if (songDetails.track_id) {
        fetch('/like', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: getUserId(),
                user_name: getUserName(),
                track_id: songDetails.track_id,
                is_add_by_user: false,
                recommendation_type: songItem.querySelector('.track-source-text').textContent
            })
        })
        .then(response => {
            if (response.status === 404) {
                handleUnauthorizedUser();
            }
            return response.json();
        })
        .then(data => {
            if (data.affected_rows > 0) {
                handle_counter()
                console.log('Song liked:', data);
            } else {
                alert(data.message);
            }
            songItem.remove();
        })
        .catch(error => {
            console.error('Error:', error);
        });
    } else {
        alert('This is not a Spotify song link.');
    }
}

function dislikeSong(button) {
    let songItem = button.parentNode.parentNode;
    let songDetails = {
        track_id: songItem.querySelector('.track-id').textContent,
        track_name: songItem.querySelector('.track-name').textContent,
        artist_name: songItem.querySelector('.artist-name').textContent,
        year: songItem.querySelector('.year').textContent.replace('(', '').replace(')', '')
    };
    appendSongToDisliked(songDetails);
    songItem.remove();

    // update database
    fetch('/dislike', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: getUserId(),
            user_name: getUserName(),
            track_id: songDetails.track_id,
            is_add_by_user: false,
            recommendation_type: songItem.querySelector('.track-source-text').textContent
        })
    })
    .then(response => {
        if (response.status === 404) {
            handleUnauthorizedUser();
        }
        return response.json();
    })
    .then(data => {
        handle_counter();
        console.log('Song disliked:', data);
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

function handle_counter() {
    user_like_or_dis_clicks_count = user_like_or_dis_clicks_count + 1
    if (user_like_or_dis_clicks_count == recommendation_list_size) {
        refreshRecommendedSongs()
    }
}

function removeSongFromList(button, listType) {
    let songItem = button.parentNode.parentNode;
    songItem.parentNode.removeChild(songItem);
    // Example API call to remove the song
    fetch("/" + listType, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            user_id: getUserId(),
            user_name: getUserName(),
            track_id: songItem.querySelector('.track-id').textContent
            // TODO: track_source: songItem.querySelector('.track-source-text').textContent
        })
    })
    .then(response => {
        if (response.status === 404) {
            handleUnauthorizedUser();
        }
        return response.json();
    })
    .then(data => {
        console.log('Song removed from list:', data);
    })
    .catch(error => console.error('Error:', error));
}

function refreshLikedSongs() {
    let user_id = getUserId();
    let user_name = getUserName();

    let likedSongsList = document.getElementById('likedSongsList');
    likedSongsList.innerHTML = ''; // Clear the list
    $("#likedLoader").removeClass("hidden");
    fetch(`/like/?user_id=${user_id}&user_name=${user_name}`)
    .then(response => {
        if (response.status === 404) {
            handleUnauthorizedUser();
        }
        return response.json();
    })
    .then(data => {
        $("#likedLoader").addClass("hidden");
        if (data.length > 0) {
            data.forEach(song => appendSongToLiked(song));
        }
    })
    .catch(error => console.error('Error:', error));
}

function refreshDislikedSongs() {
    let user_id = getUserId();
    let user_name = getUserName();

    let dislikedSongsList = document.getElementById('dislikedSongsList');
    dislikedSongsList.innerHTML = ''; // Clear the list
    $("#dislikedLoader").removeClass("hidden");

    fetch(`/dislike/?user_id=${user_id}&user_name=${user_name}`)
    .then(response => {
        if (response.status === 404) {
            handleUnauthorizedUser();
        }
        return response.json();
    })
    .then(data => {
        $("#dislikedLoader").addClass("hidden");
        if (data.length > 0) {
            data.forEach(song => appendSongToDisliked(song));
        }
    })
    .catch(error => console.error('Error:', error));
}

function refreshRecommendedSongs(is_from_button= false) {
    let user_id = getUserId();
    let user_name = getUserName();

    let recommendedSongsList = document.getElementById('recommendedSongsList');
    recommendedSongsList.innerHTML = ''; // Clear the list
    $("#recommendationsLoader").removeClass("hidden");

    is_user_ignored_recommendations = (user_like_or_dis_clicks_count === 0)
    fetch(`/recommendation/?user_id=${user_id}&user_name=${user_name}&is_from_button=${is_from_button}&is_user_ignored_recommendations=${is_user_ignored_recommendations}`)
    .then(response => {
        if (response.status === 404) {
            handleUnauthorizedUser();
        }
        return response.json();
    })
    .then(data => {
        $("#recommendationsLoader").addClass("hidden");
        if (data.length > 0) {
            recommendation_list_size = data.length
            data.forEach(song => appendSongToRecommendations(song));
        }
    })
    .catch(error => {
        $("#recommendationsLoader").addClass("hidden");
        console.error('Error:', error);
    });
}

function refreshScreen() {
    let user_id = getUserId();
    let user_name = getUserName();
    if (user_id) {
        $("#username").text(user_name);
        refreshLikedSongs();
        refreshDislikedSongs();
        refreshRecommendedSongs();
    }
}

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
    })
    .then(response => {
       return response.ok;
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

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('logoutBtn').addEventListener('click', function() {
        localStorage.removeItem(CACHE_USER_ID_KEY);
        localStorage.removeItem(CACHE_USER_NAME_KEY);
        window.location.href = '/';
    });

    document.getElementById('csvFileInput').addEventListener('change', function(event) {
        let file = event.target.files[0];
        let reader = new FileReader();

        reader.onload = function(event) {
            let csvData = event.target.result;
            processCSVData(csvData);
        };

        reader.readAsText(file);
    });

    refreshScreen();
});

// Check if user is logged in
const user_id = localStorage.getItem('user_id');
verifyUser().then(isVerified => {
    if (!isVerified) {
        handleUnauthorizedUser()
    }
});