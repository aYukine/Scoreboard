document.addEventListener('DOMContentLoaded', () => {
  // Load team info from local storage
  const team1Info = localStorage.getItem('team1')
  const team2Info = localStorage.getItem('team2')

  if (team1Info) {
    const [name, logo] = team1Info.split(',')
    document.getElementById('team1-name').value = team1Info
    document.getElementById('team1-logo').src = logo
  }

  if (team2Info) {
    const [name, logo] = team2Info.split(',')
    document.getElementById('team2-name').value = team2Info
    document.getElementById('team2-logo').src = logo
  }
})

function updateTeamInfo(team) {
  const selectElement = document.getElementById(`${team}-name`)
  const selectedValue = selectElement.value
  const [name, logo] = selectedValue.split(',')

  // Update logo
  document.getElementById(`${team}-logo`).src = logo

  // Store in local storage
  localStorage.setItem(team, selectedValue)
}

document.addEventListener('DOMContentLoaded', function () {
  function updateDisplayScores() {
    const team1TotalScore = localStorage.getItem('team1TotalScore') || 0
    const team2TotalScore = localStorage.getItem('team2TotalScore') || 0

    document.getElementById('team1-total-score').innerText = team1TotalScore
    document.getElementById('team2-total-score').innerText = team2TotalScore
  }

  setInterval(updateDisplayScores, 1000)
})

function updateTimerDisplay(timerId) {
  let timeLeft = parseInt(localStorage.getItem('timer' + timerId + 'TimeLeft'), 10)
  let duration = timerId === 1 ? 10 : 180
  let percentage = ((duration - timeLeft) / duration) * 100
  let minutes = Math.floor(timeLeft / 60)
  let seconds = timeLeft % 60
  document.getElementById('timer' + timerId + '-display').style.setProperty('--percentage', percentage + '%')
  document.querySelector('#timer' + timerId + '-display .timer-inner').textContent = `${minutes}:${seconds < 10 ? '0' + seconds : seconds}`

  if (timerId === 1 && localStorage.getItem('overlayVisible') === 'true') {
    document.getElementById('overlay-time').textContent = `${minutes}:${seconds < 10 ? '0' + seconds : seconds}`
    document.getElementById('overlay').classList.remove('hidden')
  }
}

function checkTimerStatus(timerId) {
  if (localStorage.getItem('timer' + timerId + 'Running') === 'true') {
    startDisplayTimer(timerId)
  } else {
    stopDisplayTimer(timerId)
    if (timerId === 1 && localStorage.getItem('overlayVisible') !== 'true') {
      document.getElementById('overlay').classList.add('hidden')
    }
  }
}

function startDisplayTimer(timerId) {
  if (displayTimers[timerId]) clearInterval(displayTimers[timerId])
  displayTimers[timerId] = setInterval(() => {
    updateTimerDisplay(timerId)
  }, 1000)
}

function stopDisplayTimer(timerId) {
  if (displayTimers[timerId]) clearInterval(displayTimers[timerId])
}

function closeOverlay() {
  localStorage.setItem('timer1TimeLeft', 10)
  localStorage.setItem('timer1Running', 'false')
  localStorage.setItem('overlayVisible', 'false')
  updateTimerDisplay(1)

  document.getElementById('overlay').classList.add('hidden')

  window.dispatchEvent(
    new StorageEvent('storage', {
      key: 'timer1TimeLeft',
      newValue: '60',
    })
  )
  window.dispatchEvent(
    new StorageEvent('storage', {
      key: 'timer1Running',
      newValue: 'false',
    })
  )
  window.dispatchEvent(
    new StorageEvent('storage', {
      key: 'overlayVisible',
      newValue: 'false',
    })
  )
}

window.addEventListener('storage', (event) => {
  if (event.key.startsWith('timer') && event.key.endsWith('TimeLeft')) {
    let timerId = parseInt(event.key.match(/\d+/)[0], 10)
    updateTimerDisplay(timerId)
  }
  if (event.key.startsWith('timer') && event.key.endsWith('Running')) {
    let timerId = parseInt(event.key.match(/\d+/)[0], 10)
    checkTimerStatus(timerId)
  }
  if (event.key === 'overlayVisible') {
    if (localStorage.getItem('overlayVisible') === 'true') {
      document.getElementById('overlay').classList.remove('hidden')
    } else {
      document.getElementById('overlay').classList.add('hidden')
    }
  }
})

window.onload = function () {
  ;[1, 2].forEach((timerId) => {
    updateTimerDisplay(timerId)
    checkTimerStatus(timerId)
  })
}
