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
    
    rows.forEach(row => {
        var columns = row.split(',');
        if (columns.length === headers.length) {
            console.log(columns);  // Replace this with actual processing or display logic
        } else {
            console.error('Row does not match header length:', row);
        }
    });
}

function addSong() {
    var songInput = document.getElementById('songInput').value.trim();
    if (songInput) {
        appendSongToLiked({
            song: songInput,
            artist: 'Artist Name',
            album: 'Album Name',
            year: '2021',
            link: 'https://open.spotify.com/track/exampleLink'
        }); // Append song to liked list dynamically
        
        // Example API call to save the song
        fetch('/api/addSong', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ song: songInput })
        }).then(response => response.json())
          .then(data => console.log(data))
          .catch(error => console.error('Error:', error));

        document.getElementById('songInput').value = ''; // Clear input field
    } else {
        alert('Please enter a song link or upload a CSV file.');
    }
}

function generateSongHTML({ track_id, song, artist, album, year, link }, actions) {
    return `
        <div class="list-group-item">
            <div class="item-details">
                <span class="song-id hidden">${track_id}</span>
                <span class="song-title">${song}</span>
                <span class="artist-name">${artist}</span>
                <span class="album-name">${album}</span>
                <span class="release-year">(${year})</span>
                <a href="${link}" target="_blank" class="listen-link">Listen on Spotify</a>
            </div>
            <div class="button-group">
                ${actions}
            </div>
        </div>
    `;
}

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
        track_id: songItem.querySelector('.song-id').textContent,
        song: songItem.querySelector('.song-title').textContent,
        artist: songItem.querySelector('.artist-name').textContent,
        album: songItem.querySelector('.album-name').textContent,
        year: songItem.querySelector('.release-year').textContent.replace('(', '').replace(')', ''),
        link: songItem.querySelector('.listen-link').href
    };

    appendSongToLiked(songDetails);
    songItem.remove();

//    var trackId = extractTrackId(songDetails.link);
//    if (!trackId) {
//        console.error('Invalid Spotify link:', songDetails.link);
//        return;
//    }

    // API call to like the song
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
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

function dislikeSong(button) {
    var songItem = button.parentNode.parentNode;
    var songDetails = {
        track_id: songItem.querySelector('.song-id').textContent,
        song: songItem.querySelector('.song-title').textContent,
        artist: songItem.querySelector('.artist-name').textContent,
        album: songItem.querySelector('.album-name').textContent,
        year: songItem.querySelector('.release-year').textContent.replace('(', '').replace(')', ''),
        link: songItem.querySelector('.listen-link').href
    };
    appendSongToDisliked(songDetails);
    songItem.remove();

    // API call to dislike the song
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
                    track_id: songItem.querySelector('.song-id').textContent
                })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Song removed from list');
     })
     .catch(error => console.error('Error:', error));
}

function refreshLikedSongs(user_id) {
    fetch("/like/" + user_id)
    .then(response => response.json())
    .then(data => {
        var likedSongsList = document.getElementById('likedSongsList');
        likedSongsList.innerHTML = ''; // Clear the list
        data.forEach(song => appendSongToLiked(song));
    })
    .catch(error => console.error('Error:', error));
}

function refreshDislikedSongs(user_id) {
    fetch("/dislike/" + user_id)
    .then(response => response.json())
    .then(data => {
        var dislikedSongsList = document.getElementById('dislikedSongsList');
        dislikedSongsList.innerHTML = ''; // Clear the list
        data.forEach(song => appendSongToDisliked(song));
    })
    .catch(error => console.error('Error:', error));
}

function refreshRecommendedSongs(user_id) {


}
// Example: Load recommended songs
var recommendedSongs = [
    { track_id: '0XFvyWMTdl5DKSwbsWLm7n', song: 'Song 1', artist: 'Artist 1', album: 'Album 1', year: '2021', link: 'https://open.spotify.com/track/3d9DChrdc6BOeFsbrZ3Is0' },
    { track_id: '2WDXWl2o1lrH6Bcq7xVagu', song: 'Song 2', artist: 'Artist 2', album: 'Album 2', year: '2020', link: 'https://open.spotify.com/track/5qqabIl2vWzo9ApSC317sa' },
    { track_id: '6amT1NV7Ag2SPOdbqdnhFb', song: 'Song 3', artist: 'Artist 2', album: 'Album 2', year: '2020', link: 'https://open.spotify.com/track/48UPSzbZjgc449aqz8bxox' }
];
recommendedSongs.forEach(song => appendSongToRecommendations(song));

user_id = 2
refreshLikedSongs(user_id)
refreshDislikedSongs(user_id)
refreshRecommendedSongs(user_id)