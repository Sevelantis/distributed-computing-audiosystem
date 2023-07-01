const server = 'http://localhost:8888'
var dragEvents = null
var dragHighlight = null
var dragUnighlight = null
var inputRange = null
var dropArea = null
var progressBar = null
var iconElement = null
var editorElement = null
var chooseMp3Button = null
var progressLabel = null
var progressLabel = null
var switchDrums = null
var switchBass = null
var switchVocals = null
var switchOther = null
var progressLabel = null
var musicIdLabel = null
var songNameLabel = null
var bandLabel = null
var submittedMusic = null
var btnDownloadDrums = null
var btnDownloadBass = null
var btnDownloadVocals = null
var btnDownloadOther = null
var btnDownloadMix = null
var downloadBtns = null
var processTimeBadge = null
var musicContainer = null

window.addEventListener('DOMContentLoaded', () => {
  dragEvents = ["dragenter", "dragover", "dragleave", "drop"];
  dragHighlight = ["dragenter", "dragover"];
  dragUnighlight = ["dragleave", "drop"];
  inputRange = document.querySelectorAll(".editor input");

  dropArea = document.getElementById("drop-area");
  progressBar = document.getElementById("progressbar");
  progressLabel = document.getElementById("progressLabel")
  iconElement = document.querySelector(".circle");
  chooseMp3Button = document.getElementById("chooseMp3Button")
  editorElement = document.querySelector(".editor");
  switchDrums = document.getElementById('switchDrums')
  switchBass = document.getElementById('switchBass')
  switchVocals = document.getElementById('switchVocals')
  switchOther = document.getElementById('switchOther')
  progressLabel = document.getElementById('progressLabel')
  submittedMusic = document.getElementById('submittedMusic')
  // musicIdLabel = document.getElementById('musicIdLabel')
  // songNameLabel = document.getElementById('songNameLabel')
  // bandLabel = document.getElementById('bandLabel')
  btnDownloadDrums = document.getElementById('btnDownloadDrums')
  btnDownloadBass = document.getElementById('btnDownloadBass')
  btnDownloadVocals = document.getElementById('btnDownloadVocals')
  btnDownloadOther = document.getElementById('btnDownloadOther')
  btnDownloadMix = document.getElementById('btnDownloadMix')
  downloadBtns = document.getElementById('downloadBtns')
  processTimeBadge = document.getElementById('processTimeBadge')
  musicContainer = document.getElementById('musicContainer')

  const highlight = () => {
    iconElement.classList.add("highlight");
  };

  const unhighlight = () => {
    iconElement.classList.remove("highlight");
  };

  preventDefaults = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };
  inputRange.forEach((input) => input.addEventListener("change", handleUpdate));
  inputRange.forEach((input) =>
    input.addEventListener("mousemove", handleUpdate)
  );

  dragEvents.forEach((eventName) => {
    dropArea.addEventListener(eventName, preventDefaults, false);
  });

  dragHighlight.forEach((eventName) => {
    dropArea.addEventListener(eventName, highlight, false);
  });

  dragUnighlight.forEach((eventName) => {
    dropArea.addEventListener(eventName, unhighlight, false);
  });

  btnDownloadDrums.addEventListener('click', function () {
    window.location.href = btnDownloadDrums.getAttribute('href');;
  });
  btnDownloadBass.addEventListener('click', function () {
    window.location.href = btnDownloadBass.getAttribute('href');;
  });
  btnDownloadVocals.addEventListener('click', function () {
    window.location.href = btnDownloadVocals.getAttribute('href');;
  });
  btnDownloadOther.addEventListener('click', function () {
    window.location.href = btnDownloadOther.getAttribute('href');;
  });
  btnDownloadMix.addEventListener('click', function () {
    window.location.href = btnDownloadMix.getAttribute('href');;
  });

  dropArea.addEventListener('drop', function (event) {
    event.preventDefault();
    handleDrop(event.dataTransfer.files);
  });
});

function handleUpdate() {
  console.log(this.value);
  const suffix = this.dataset.unit;
  document.documentElement.style.setProperty(
    `--${this.name}`,
    this.value + suffix
  );
}

const handleDrop = (files) => {
  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    formData.append('body', files[i]);
  }
  submitMusic(formData);
};


async function submitMusic(formData) {
  await fetch(`${server}/music`, {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      test(data)
      progressBar.setAttribute('aria-valuenow', 0);
      progressLabel.innerHTML = 'Progress: 0%';
      progressBar.setAttribute('style', 'width: 0%');
      progressLabel.classList.add('progress-font-size');
      progressBar.classList.remove('d-none');
      chooseMp3Button.classList.add('d-none');
      switchDrums.disabled = true;
      switchBass.disabled = true;
      switchVocals.disabled = true;
      switchOther.disabled = true;
      processMusic(data)
    })
    .catch(error => {
      console.error(error);
    });

  return false;
}

async function test(music) {
  console.log(music)
}

async function processMusic(music) {
  try {
    musicId = music["music_id"]
    band = music['band']
    songName = music['name']
    tracks = music['tracks']

    checked_tracks = []
    for (let i = 0; i < tracks.length; i++) {
      const track = tracks[i];
      if (track['name'] === 'drums' && switchDrums.checked) {
        checked_tracks.push(track.track_id)
      }
      if (track['name'] === 'bass' && switchBass.checked) {
        checked_tracks.push(track.track_id)
      }
      if (track['name'] === 'vocals' && switchVocals.checked) {
        checked_tracks.push(track.track_id)
      }
      if (track['name'] === 'other' && switchOther.checked) {
        checked_tracks.push(track.track_id)
      }
    }
    console.log('checked trucks: ' + JSON.stringify(checked_tracks))

    const newMusicRowHtml = `
      <div class="row">
        <div class="col-2 text-center">${musicId}</div>
        <div class="col-sm text-center ">${songName}</div>
        <div class="col-sm text-center">${band}</div>
      </div>
    `;
    submittedMusic.insertAdjacentHTML('beforeend', newMusicRowHtml);
    musicContainer.classList.remove('d-none')

    await fetch(`${server}/music/${musicId}`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(checked_tracks)
      })
      .then(response => response.json())
      .then(data => {
        updateProgress(musicId)
      })
      .catch(error => {
        console.error(error);
      });

    return false;
  } catch (error) {
    console.error(error);
  }
}

function updateProgress(musicId) {
  const intervalId = setInterval(() => {
    // Make a GET request to retrieve the progress
    fetch(`${server}/music/${musicId}`)
      .then(response => response.json())
      .then(data => {
        progressBar.setAttribute('aria-valuenow', data['progress']);
        progressBar.setAttribute('style', `width: ${data['progress']}%;`);
        progressBar.classList.toggle('refresh');
        progressLabel.innerHTML = `Progress: ${data['progress']}%`;
        console.log('current progress: ' + JSON.stringify(data));
        if (data['progress'] === 100) {
          clearInterval(intervalId);
          processingDone(data)
        }
      })
      .catch(error => {
        console.error('Error retrieving progress:', error);
      });
  }, 500); // Update the progress every 500ms
}

function processingDone(data) {
  dropArea.classList.add('d-none');
  downloadBtns.classList.remove('d-none')

  instruments = data['instruments']
  for (let i = 0; i < instruments.length; i++) {
    const instr = instruments[i];
    console.log('instr['+i+']: '+ JSON.stringify(instr))
    if (instr['name'] === 'drums') {
      console.log(instr['track'])
      btnDownloadDrums.setAttribute('href', instr['track'])
    }
    if (instr['name'] === 'bass') {
      console.log(instr['track'])
      btnDownloadBass.setAttribute('href', instr['track'])
    }
    if (instr['name'] === 'vocals') {
      console.log(instr['track'])
      btnDownloadVocals.setAttribute('href', instr['track'])
    }
    if (instr['name'] === 'other') {
      console.log(instr['track'])
      btnDownloadOther.setAttribute('href', instr['track'])
    }
  }
  btnDownloadMix.setAttribute('href', data['final'])
}

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  
  const minutesString = String(minutes).padStart(2, '0');
  const secondsString = String(remainingSeconds).padStart(2, '0');
  
  return `${minutesString}:${secondsString}`;
}
