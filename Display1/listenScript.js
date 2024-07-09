const socket = new WebSocket('ws://localhost:8991');

socket.onopen = function (event) {
  console.log("WebSocket connection opened");
};

socket.onmessage = function (event) {
  const scoreData = JSON.parse(event.data);
  updateScores(scoreData);
};

socket.onerror = function (event) {
  console.error("WebSocket error:", event);
};

function changeCircleColor(circleId, newColor) {
  const circleElement = document.getElementById(circleId);

  if (circleElement) {
    circleElement.style.backgroundColor = newColor;
  } else {
    console.error(`Circle with ID '${circleId}' not found.`);
  }
}

function updateInfo(team, png_name, name){
  logo = `/public/TeamLogo/${png_name}.png` 
  document.getElementById(`${team}-logo`).src = logo
  document.getElementById(`${team}-name`).textContent = name
}

function updateScores(data) {
  document.getElementById("team1-total-score").textContent = data.plant1*10 + data.harvest1*10 + data.store1*30;
  document.getElementById("team2-total-score").textContent = data.plant2*10 + data.harvest2*10 + data.store2*30;
  for(let i=0;i<5;i++){
    data.silos[i].forEach((ball, index )=> {
      if(ball==1){c = "red"}
      else if(ball==2){c="blue"}
      else{c=""}
      changeCircleColor(`s${i+1}-${index+1}`, c)
    });
  }
  updateInfo("team1", data.team1[0], data.team1[1])
  updateInfo("team2", data.team2[0], data.team2[1])
  document.getElementById("timerd").textContent = data.time;
}