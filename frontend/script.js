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

function generateSongHTML({ song, artist, album, year, link }, actions) {
    return `
        <div class="list-group-item">
            <div class="item-details">
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
    var actions = `<button class="btn btn-danger" onclick="removeSongFromList(this, 'liked')"><i class="fa fa-trash"></i> Remove</button>`;
    likedSongsList.innerHTML += generateSongHTML(songDetails, actions);
}

function appendSongToRecommendations(songDetails) {
    var recommendedSongsList = document.getElementById('recommendedSongsList');
    var actions = `
        <button class="btn btn-success" onclick="likeSong(this)"><i class="fa fa-thumbs-up"></i> Like</button>
        <button class="btn btn-danger" onclick="dislikeSong(this)"><i class="fa fa-thumbs-down"></i> Dislike</button>
    `;
    recommendedSongsList.innerHTML += generateSongHTML(songDetails, actions);
}

function appendSongToDisliked(songDetails) {
    var dislikedSongsList = document.getElementById('dislikedSongsList');
    var actions = `<button class="btn btn-danger" onclick="removeSongFromList(this, 'disliked')"><i class="fa fa-trash"></i> Remove</button>`;
    dislikedSongsList.innerHTML += generateSongHTML(songDetails, actions);
}

function likeSong(button) {
    var songItem = button.parentNode.parentNode;
    var songDetails = {
        song: songItem.querySelector('.song-title').textContent,
        artist: songItem.querySelector('.artist-name').textContent,
        album: songItem.querySelector('.album-name').textContent,
        year: songItem.querySelector('.release-year').textContent.replace('(', '').replace(')', ''),
        link: songItem.querySelector('.listen-link').href
    };
    appendSongToLiked(songDetails);
    songItem.remove();
}

function dislikeSong(button) {
    var songItem = button.parentNode.parentNode;
    var songDetails = {
        song: songItem.querySelector('.song-title').textContent,
        artist: songItem.querySelector('.artist-name').textContent,
        album: songItem.querySelector('.album-name').textContent,
        year: songItem.querySelector('.release-year').textContent.replace('(', '').replace(')', ''),
        link: songItem.querySelector('.listen-link').href
    };
    appendSongToDisliked(songDetails);
    songItem.remove();
}

function removeSongFromList(button, listType) {
    var songItem = button.parentNode.parentNode;
    songItem.parentNode.removeChild(songItem);
    // Example API call to remove the song
    fetch('/api/removeSong', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ song: songItem.querySelector('.song-title').textContent, list: listType })
    }).then(response => response.json())
      .then(data => console.log(data))
      .catch(error => console.error('Error:', error));
}

function refreshLikedSongs() {
    // Example API call to get liked songs
    fetch('/api/getLikedSongs')
    .then(response => response.json())
    .then(data => {
        var likedSongsList = document.getElementById('likedSongsList');
        likedSongsList.innerHTML = ''; // Clear the list
        data.forEach(song => appendSongToLiked(song));
    })
    .catch(error => console.error('Error:', error));
}

// Example: Load recommended songs
var recommendedSongs = [
    { song: 'Song 1', artist: 'Artist 1', album: 'Album 1', year: '2021', link: 'https://open.spotify.com/track/exampleLink1' },
    { song: 'Song 2', artist: 'Artist 2', album: 'Album 2', year: '2020', link: 'https://open.spotify.com/track/exampleLink2' }
];
recommendedSongs.forEach(song => appendSongToRecommendations(song));
