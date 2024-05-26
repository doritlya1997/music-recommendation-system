CACHE_USER_ID_KEY = 'user_id'
CACHE_USER_NAME_KEY = 'user_name'

function getUserId() {
    id = localStorage.getItem(CACHE_USER_ID_KEY)
    return id ? Number(id) : null
}
function getUserName() {
    return localStorage.getItem(CACHE_USER_NAME_KEY)
}

document.getElementById('logoutBtn').addEventListener('click', function() {
            localStorage.removeItem(CACHE_USER_ID_KEY);
            window.location.href = '/';
        });

document.getElementById('csvFileInput').addEventListener('change', function(event) {
    var file = event.target.files[0];
    var reader = new FileReader();
    
    reader.onload = function(event) {
        var csvData = event.target.result;
        processCSVData(csvData);
    };

    reader.readAsText(file);
});

function processCSVData(csvData) {
    var dataLines = csvData.split(/\r\n|\n/);
    if (dataLines.length <= 1) {
        alert('The CSV file is empty or improperly formatted.');
        return;
    }
    var headers = dataLines[0].split(',');
    var rows = dataLines.slice(1);

    track_id_list = []
    error_occurred = null
    rows.forEach(row => {
        if (!error_occurred) {
            var columns = row.split(',');
            if (columns.length === headers.length) {
                track_id_list.push(columns[0]);
            } else {
                alert('CSV Row does not match header length:', row);
                error_occurred = true
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
                track_ids: track_id_list
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.affected_rows > 0)
                alert(data.affected_rows + " " + data.message)
            else
                alert(data.message)
            console.log('Songs liked:', data);
            refreshLikedSongs();
        })
        .catch(error => console.error('Error:', error));

        document.getElementById('songInput').value = ''; // Clear input field

     }
}

function addSong() {
    var song_input = document.getElementById('songInput').value.trim();
    track_id = extractTrackId(song_input)

    if (track_id) {
        fetch('/like', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: getUserId(),
                track_id: track_id
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Song liked:', data);
            refreshLikedSongs();
        })
        .catch(error => console.error('Error:', error));

        document.getElementById('songInput').value = '';
    } else {
        alert('Please enter a Spotify song link or upload a CSV file.');
    }
}

function generateSongHTML({ track_id, track_name, artist_name, year, link }, actions) {
    return `
        <div class="list-group-item">
            <div class="item-details">
                <span class="track-id hidden">${track_id}</span>
                <span class="track-name">${track_name}</span>
                <span class="artist-name">${artist_name}</span>
                <span class="year">(${year})</span>
                <a href="${link}" target="_blank" class="listen-link">Listen on Spotify</a>
            </div>
            <div class="button-group">
                ${actions}
            </div>
        </div>
    `;
}
// TODO: append at the beginning
function appendSongToLiked(songDetails) {
    var likedSongsList = document.getElementById('likedSongsList');
    var actions = `<button class="btn btn-danger" onclick="removeSongFromList(this, 'like')"><i class="fa fa-trash"></i> Remove</button>`;
    likedSongsList.innerHTML += generateSongHTML(songDetails, actions);
}

function appendSongToDisliked(songDetails) {
    var dislikedSongsList = document.getElementById('dislikedSongsList');
    var actions = `<button class="btn btn-danger" onclick="removeSongFromList(this, 'dislike')"><i class="fa fa-trash"></i> Remove</button>`;
    dislikedSongsList.innerHTML += generateSongHTML(songDetails, actions);
}

function appendSongToRecommendations(songDetails) {
    var recommendedSongsList = document.getElementById('recommendedSongsList');
    var actions = `
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
    var songItem = button.parentNode.parentNode;
    var songDetails = {
        track_id: songItem.querySelector('.track-id').textContent,
        track_name: songItem.querySelector('.track-name').textContent,
        artist_name: songItem.querySelector('.artist-name').textContent,
        year: songItem.querySelector('.year').textContent.replace('(', '').replace(')', ''),
        link: songItem.querySelector('.listen-link').href
    };

    appendSongToLiked(songDetails);
    songItem.remove();

    // update database
    fetch('/like', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: user_id,
            track_id: songDetails.track_id
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Song liked:', data);
        refreshLikedSongs();
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

function dislikeSong(button) {
    var songItem = button.parentNode.parentNode;
    var songDetails = {
        track_id: songItem.querySelector('.track-id').textContent,
        song: songItem.querySelector('.track-name').textContent,
        artist: songItem.querySelector('.artist-name').textContent,
        year: songItem.querySelector('.year').textContent.replace('(', '').replace(')', ''),
        link: songItem.querySelector('.listen-link').href
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
            user_id: user_id,
            track_id: songDetails.track_id
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Song disliked:', data);
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

function removeSongFromList(button, listType) {
    var songItem = button.parentNode.parentNode;
    songItem.parentNode.removeChild(songItem);
    // Example API call to remove the song
    fetch("/" + listType, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
                    user_id: user_id,
                    track_id: songItem.querySelector('.track_id').textContent
                })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Song removed from list');
     })
     .catch(error => console.error('Error:', error));
}

function refreshLikedSongs() {
    var user_id = getUserId()

    fetch("/like/" + user_id)
    .then(response => response.json())
    .then(data => {
        var likedSongsList = document.getElementById('likedSongsList');
        likedSongsList.innerHTML = ''; // Clear the list
        data.forEach(song => appendSongToLiked(song));
    })
    .catch(error => console.error('Error:', error));
}

function refreshDislikedSongs() {
    var user_id = getUserId()

    fetch("/dislike/" + user_id)
    .then(response => response.json())
    .then(data => {
        var dislikedSongsList = document.getElementById('dislikedSongsList');
        dislikedSongsList.innerHTML = ''; // Clear the list
        data.forEach(song => appendSongToDisliked(song));
    })
    .catch(error => console.error('Error:', error));
}

function refreshRecommendedSongs() {
    var user_id = getUserId()

    var recommendedSongsList = document.getElementById('recommendedSongsList');
    recommendedSongsList.innerHTML = ''; // Clear the list
    $("#recommendationsLoader").removeClass("hidden");

    fetch("/recommendation/" + user_id)
    .then(response => response.json())
    .then(data => {
        $("#recommendationsLoader").addClass("hidden");
        data.forEach(song => appendSongToRecommendations(song));
    })
    .catch(error => console.error('Error:', error));
}

// Check if user is logged in
const user_id = localStorage.getItem('user_id');
if (!user_id) {
    window.location.href = '/';
};


function refreshScreen() {
    var user_id = getUserId()
    var user_name = getUserName()
    if (user_id) {
        $("#username").text(user_name)
        refreshLikedSongs()
        refreshDislikedSongs()
        refreshRecommendedSongs()
    }
}

refreshScreen()