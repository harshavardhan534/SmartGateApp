function sendLocation(){

    if(!navigator.geolocation){

        alert("Geolocation not supported");
        return;

    }

    navigator.geolocation.getCurrentPosition(

        success,

        error,

        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
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

        alert(
            "Gate Status: " + data.status
        );

        location.reload();

    });

}

function error(err){

    if(err.code === 1){

        alert("Location permission denied");

    }

    else if(err.code === 2){

        alert("Location unavailable");

    }

    else if(err.code === 3){

        alert("Location request timed out");

    }

    else{

        alert("Unknown GPS error");

    }

}