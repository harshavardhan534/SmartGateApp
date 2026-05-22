// -----------------------------------
// AUTO LOCATION TRACKING
// -----------------------------------

function sendLocation(position) {

    const data = {
        lat: position.coords.latitude,
        lon: position.coords.longitude,
        speed: position.coords.speed || 0
    };

    fetch("/location", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log("Location Sent:", data);
    })
    .catch(error => {
        console.log("Error:", error);
    });
}

// -----------------------------------
// LOCATION ERROR
// -----------------------------------

function locationError(error) {

    alert("Please Enable Location Permission and GPS");
}

// -----------------------------------
// AUTO START LOCATION
// -----------------------------------

if (navigator.geolocation) {

    navigator.geolocation.watchPosition(
        sendLocation,
        locationError,
        {
            enableHighAccuracy: true,
            maximumAge: 0,
            timeout: 10000
        }
    );

} else {

    alert("Geolocation is not supported");
}
