function sendLocation(){

    navigator.geolocation.getCurrentPosition(
        success,
        error,
        {
            enableHighAccuracy: true
        }
    );

}

function success(position){

    let data = {

        lat: position.coords.latitude,
        lon: position.coords.longitude,
        speed: position.coords.speed || 0

    };

    fetch('/location', {

        method:'POST',

        headers:{
            'Content-Type':'application/json'
        },

        body: JSON.stringify(data)

    })

    .then(response => response.json())

    .then(data => {

        document.getElementById("gate").innerHTML =
            data.gate;

        document.getElementById("distance").innerHTML =
            data.distance + " meters";

        document.getElementById("status").innerHTML =
            data.status;

    });

}

function error(){

    alert("Location permission denied");

}

# AUTO REFRESH EVERY 5 SECONDS
setInterval(sendLocation, 5000);
