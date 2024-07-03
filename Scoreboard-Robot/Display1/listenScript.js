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

function updateScores(data) {
    document.getElementById("team1-total-score").textContent = data.plant1*10 + data.harvest1*10 + data.store1*30;
    document.getElementById("team2-total-score").textContent = data.plant2*10 + data.harvest2*10 + data.store2*30;
    for(let i=0;i<5;i++){
        data.silos[i].forEach((ball, index )=> {
          if(ball==1){c = "red"}
          else{c="blue"}
          changeCircleColor(`s${i+1}-${index+1}`, c)
        });
    }
}