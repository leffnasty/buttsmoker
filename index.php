<?php
    $servername = "localhost";
    $username = "smoker";
    $password = "sauceman";
    $dbname = "MY_SMOKER";

    function debug_to_console($data) {
        $output = $data;
        if (is_array($output))
            $output = implode(',', $output);
    
        echo "<script>console.log('Debug Objects: " . $output . "' );</script>";
    }


    // Create connection
    $conn = new mysqli($servername, $username, $password, $dbname);
    // Check connection
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }


    $sql = "SELECT id, time, pit_temp, meat_temp FROM TempLog ORDER BY id DESC";
    $result = $conn->query($sql);

    $tempSet = "SELECT set_temp, done_temp FROM ParameterLog ORDER BY id DESC LIMIT 1";
    $settingResult = $conn->query($tempSet);
    $settingResultRow = $settingResult->fetch_assoc()
?>

<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>butt-smoker</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <link href="https://fonts.googleapis.com/css?family=Exo:300,400,700,800&display=swap" rel="stylesheet">
    <link rel="stylesheet" type="text/css" media="screen" href="main.css" />
</head>
<body>
    <main class="main-content">

        <h1>Butt-smoker</h1>

        <div class="upper-content">
            <div class="upper-content-section">
                <div class="temp-settings-field">
                    <label for="setTemp">Set Point Temperature</label>
                    <?php echo "<input type='text' name='setTemp' id='setTemp' placeholder='Set Point Temperature' value='" . $settingResultRow["set_temp"] . "'>" ?>
                </div>
                <div class="temp-settings-field">
                    <label for="doneTemp">Done Temperature</label>
                    <?php echo "<input type='text' name='doneTemp' id='doneTemp' placeholder='Done Temperature' value='" . $settingResultRow["done_temp"] . "'>" ?>
                </div>
            </div>
            <div class="upper-content-section">
                <canvas id="line-chartcanvas"></canvas>
            </div>
        </div>

        <div class="table">
            <div class="thead">
                <div class="tr">
                    <div class="th-cell">Row Number</div>
                    <div class="th-cell">Time</div>
                    <div class="th-cell">Pit Temperature</div>
                    <div class="th-cell">Meat Temperature</div>
                </div>
            </div>
            <div class="tbody">
                <?php
                    if ($result->num_rows > 0) {
                        // output data of each row
                        $pitTemps = array();
                        $meatTemps = array();
                        $time = array();

                        while($row = $result->fetch_assoc()) {
                            echo "<div class='tr'><div class='td-cell'>" . $row["id"]. "</div><div class='td-cell'>" . $row["time"]. "</div><div class='td-cell'>" . $row["pit_temp"]. "</div><div class='td-cell'>" . $row["meat_temp"]. "</div></div>";
                            
                            array_push($pitTemps, $row["pit_temp"]);
                            array_push($meatTemps, $row["meat_temp"]);
                            array_push($time, $row["time"]);
                        }

                    } else {
                        echo "0 results";
                    }
                ?>
            </div>
        </div>

    </main>

    <script src="https://code.jquery.com/jquery-3.4.1.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@2.8.0/dist/Chart.min.js"></script>
    
    <script>
        $(document).ready(function() {

            var pitTemps = <?php echo json_encode($pitTemps) ;?>;
            var meatTemps = <?php echo json_encode($meatTemps) ;?>;
            var time = <?php echo json_encode($time) ;?>;


            pitTemps.reverse();
            meatTemps.reverse();
            time.reverse();

            var setTemp = <?php echo $settingResultRow["set_temp"] ;?>;
            var setTemps = new Array(pitTemps.length).fill(setTemp);

            var doneTemp = <?php echo $settingResultRow["done_temp"] ;?>;
            var doneTemps = new Array(pitTemps.length).fill(doneTemp);

            //get canvas
            var ctx = $("#line-chartcanvas");

            var data = {
                labels : time,
                datasets : [
                    {
                        label : "Pit Temps",
                        data : pitTemps,
                        backgroundColor : "blue",
                        borderColor : "lightblue",
                        fill : false,
                        lineTension : 0,
                        pointRadius : 3
                    },
                    {
                        label : "Meat Temps",
                        data : meatTemps,
                        backgroundColor : "green",
                        borderColor : "lightgreen",
                        fill : false,
                        lineTension : 0,
                        pointRadius : 3
                    },
                    {
                        label : "Set Temp",
                        data : setTemps,
                        backgroundColor : "red",
                        borderColor : "pink",
                        fill : false,
                        lineTension : 0,
                        pointRadius : 0
                    },
                    {
                        label : "Done Temp",
                        data : doneTemps,
                        backgroundColor : "black",
                        borderColor : "gray",
                        fill : false,
                        lineTension : 0,
                        pointRadius : 0
                    }
                ]
            };

            var options = {
                legend : {
                    display : true,
                    position : "bottom"
                }
            };

            var chart = new Chart( ctx, {
                type : "line",
                data : data,
                options : options
            } );

            });
    </script>
</body>
</html>

<?php $conn->close(); ?>