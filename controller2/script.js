// Get references to the necessary elements
const displayText = document.getElementById('displayText')
const startGameButton = document.getElementById('startGameButton')
const pepSound = document.getElementById('pepSound')
const totalScoreElement = document.getElementById('totalScore')
const redTeamScoreElement = document.getElementById('redTeamScore')
const blueTeamScoreElement = document.getElementById('blueTeamScore')
const resetButtons = document.querySelectorAll('.reset-column-button')
const undoButtons = document.querySelectorAll('.undo-button')
const columns = document.querySelectorAll('.column')

let totalScore = 0
let redTeamScore = 0
let blueTeamScore = 0
const maxClicksPerColumn = 3

columns.forEach((column) => {
  column.clickCount = 0
  column.history = []
})

// Function to start the countdown
function startCountdown(seconds) {
  let remainingTime = seconds

  // Change text color to red
  displayText.style.color = 'red'

  // Function to update the countdown
  function updateCountdown() {
    if (remainingTime > 0) {
      // Update the display text
      displayText.textContent = remainingTime
      // Play the pep sound
      pepSound.play()
      // Decrement the remaining time
      remainingTime--
    } else {
      // Reset the text color to black and stop the countdown
      displayText.style.color = 'black'
      displayText.textContent = '---'
      clearInterval(countdownInterval)
    }
  }

  // Update the countdown immediately and then every second
  updateCountdown()
  let countdownInterval = setInterval(updateCountdown, 1000)
}

// Add event listener to startGameButton
startGameButton.addEventListener('click', function () {
  startCountdown(3)
})

// Function to update the total score
function updateTotalScore() {
  totalScore = redTeamScore + blueTeamScore
  totalScoreElement.textContent = totalScore
}

// Function to handle color button clicks
function handleColorButtonClick(color, columnElement) {
  const circles = columnElement.querySelectorAll('.circle')

  for (let i = 0; i < circles.length; i++) {
    if (!circles[i].classList.contains('red') && !circles[i].classList.contains('blue')) {
      circles[i].classList.add(color)
      if (color === 'red') {
        redTeamScore += 30
        redTeamScoreElement.textContent = redTeamScore
      } else if (color === 'blue') {
        blueTeamScore += 30
        blueTeamScoreElement.textContent = blueTeamScore
      }
      columnElement.clickCount++
      columnElement.history.push(circles[i])
      updateTotalScore()
      break
    }
  }
}

// Function to undo the last color change
function undoLastAction(columnElement) {
  const lastCircle = columnElement.history.pop()
  if (lastCircle) {
    if (lastCircle.classList.contains('red')) {
      redTeamScore -= 30
      lastCircle.classList.remove('red')
    } else if (lastCircle.classList.contains('blue')) {
      blueTeamScore -= 30
      lastCircle.classList.remove('blue')
    }
    columnElement.clickCount--
    redTeamScoreElement.textContent = redTeamScore
    blueTeamScoreElement.textContent = blueTeamScore
    updateTotalScore()
  }
}

// Function to reset a column
function resetColumn(columnElement) {
  const circles = columnElement.querySelectorAll('.circle')
  circles.forEach((circle) => {
    if (circle.classList.contains('red')) {
      redTeamScore -= 30
      circle.classList.remove('red')
    } else if (circle.classList.contains('blue')) {
      blueTeamScore -= 30
      circle.classList.remove('blue')
    }
  })
  columnElement.clickCount = 0
  columnElement.history = []
  redTeamScoreElement.textContent = redTeamScore
  blueTeamScoreElement.textContent = blueTeamScore
  updateTotalScore()
}

// Add event listeners to color buttons, undo buttons, and reset buttons
columns.forEach((column) => {
  const redButton = column.querySelector('.color-button[data-color="red"]')
  const blueButton = column.querySelector('.color-button[data-color="blue"]')
  const undoButton = column.querySelector('.undo-button')
  const resetButton = column.querySelector('.reset-column-button')

  redButton.addEventListener('click', () => {
    if (column.clickCount < maxClicksPerColumn) {
      handleColorButtonClick('red', column)
    }
  })

  blueButton.addEventListener('click', () => {
    if (column.clickCount < maxClicksPerColumn) {
      handleColorButtonClick('blue', column)
    }
  })

  undoButton.addEventListener('click', () => {
    undoLastAction(column)
  })

  resetButton.addEventListener('click', () => {
    resetColumn(column)
  })
})
