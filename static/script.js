// =========================================
// SAVE LAST LOCATION
// =========================================

let lastLat = null;
let lastLng = null;

// =========================================
// OPEN GOOGLE MAP ROUTE
// =========================================

function openRoute(destLat,destLng){

    if(lastLat == null || lastLng == null){

        alert("Waiting for GPS...");

        return;
    }

    const url =

        "https://www.google.com/maps/dir/?api=1" +

        "&origin=" +

        lastLat +

        "," +

        lastLng +

        "&destination=" +

        destLat +

        "," +

        destLng +

        "&travelmode=driving";

    window.location.href = url;
}

// =========================================
// STATUS COLORS
// =========================================

function setStatus(id,status){

    const box =
        document.getElementById(id);

    box.className = "status";

    if(status == "OPEN"){

        box.innerText = "OPEN";

        box.classList.add("open");
    }

    else if(status == "CLOSED"){

        box.innerText = "CLOSED";

        box.classList.add("closed");
    }

    else{

        box.innerText = "NO DATA";

        box.classList.add("unknown");
    }
}

// =========================================
// UPDATE LOCATION
// =========================================

function updateLocation(){

    navigator.geolocation.getCurrentPosition(

        async function(position){

            try{

                const lat =
                    position.coords.latitude;

                const lng =
                    position.coords.longitude;

                lastLat = lat;
                lastLng = lng;

                // SPEED

                let speed =
                    position.coords.speed;

                if(speed == null){

                    speed = 0;
                }

                speed = speed * 3.6;

                if(speed < 3){

                    speed = 0;
                }

                // SHOW LOCATION

                document.getElementById("locationText").innerHTML =

                    "Latitude: " +
                    lat.toFixed(5) +

                    "<br><br>Longitude: " +
                    lng.toFixed(5);

                // SHOW SPEED

                document.getElementById("speedText").innerText =

                    "Speed: " +
                    speed.toFixed(2) +
                    " km/h";

                // SEND TO SERVER

                const response = await fetch(

                    "/location",

                    {

                        method:"POST",

                        headers:{
                            "Content-Type":"application/json"
                        },

                        body:JSON.stringify({

                            lat:lat,
                            lng:lng,
                            speed:speed

                        })

                    }

                );

                const data =
                    await response.json();

                if(data.success){

                    // GATE 1

                    document.getElementById("distance1").innerText =

                        "Distance: " +
                        data.gates[0].distance +
                        " meters";

                    document.getElementById("waiting1").innerText =

                        "Waiting Users: " +
                        data.gates[0].waiting;

                    setStatus(
                        "status1",
                        data.gates[0].status
                    );

                    // GATE 2

                    document.getElementById("distance2").innerText =

                        "Distance: " +
                        data.gates[1].distance +
                        " meters";

                    document.getElementById("waiting2").innerText =

                        "Waiting Users: " +
                        data.gates[1].waiting;

                    setStatus(
                        "status2",
                        data.gates[1].status
                    );

                }

            }

            catch(error){

                console.log(error);

                document.getElementById("locationText").innerText =

                    "Server Error";
            }

        },

        function(error){

            console.log(error);

            if(lastLat != null){

                document.getElementById("locationText").innerHTML =

                    "Using Previous Location";

            }

            else{

                document.getElementById("locationText").innerHTML =

                    "Searching GPS...";
            }

        },

        {

            enableHighAccuracy:false,

            timeout:8000,

            maximumAge:15000

        }

    );

}

// FIRST LOAD

updateLocation();

// AUTO REFRESH EVERY 5 SEC

setInterval(updateLocation,5000);
