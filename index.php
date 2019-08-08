<?php
$servername = "localhost";
$username = "smoker";
$password = "sauceman";
$dbname = "MY_SMOKER";


// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
} 


$sql = "SELECT id, time, pit_temp, meat_temp FROM TempLog";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    // output data of each row
    while($row = $result->fetch_assoc()) {
        echo "id: " . $row["id"]. " - Time: " . $row["time"]. " - Pit Temp: " . $row["pit_temp"]. " - Meat Temp: " . $row["meat_temp"]. "<br>";
    }
} else {
    echo "0 results";
}

$conn->close();
?>