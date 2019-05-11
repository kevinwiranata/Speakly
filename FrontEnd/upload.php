<?php
echo '<script>showLoading();</script>';
echo "<head><title> Speakly </title><link rel=\"icon\" href=\"icon.ico\"></head><style>body { background-color: #9fc5e8ff; } </style><br /><div style='position: relative; text-align: center; color: white; font-size: 275%; top: 20%;'>";
$target_dir = "uploads/";
$target_name = basename($_FILES["fileToUpload"]["name"]);
$target_file = $target_dir . $target_name;
$uploadOk = 1;
$imageFileType = strtolower(pathinfo($target_file,PATHINFO_EXTENSION));

// Allow certain file formats
if($imageFileType != "mp4" ) {
    echo "Sorry, only MP4 files are allowed. ";
    $uploadOk = 0;
}

// Check if $uploadOk is set to 0 by an error
if ($uploadOk == 0) {
    echo "Sorry, your file was not uploaded.";echo '</div><img src="icon.ico" width="150" height="150" style="position: absolute; top: 10%; left: 5%; transform: translate(-50%, -50%);"><script>hideLoading();</script>';
// if everything is ok, try to upload file
} else {
    if (move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file)) {
        $commandScreencaps = escapeshellcmd("screencaps.py $target_name");
        $outputScreencaps = shell_exec($commandScreencaps);

        $fname = substr($target_name, 0, strlen($target_name)-4);
        $stereo_file = "audio/stereo/" . $fname . ".flac";
        $mono_file = "audio/mono/" . $fname . ".flac";
        $commandSTM = escapeshellcmd("ffmpeg -i $stereo_file -ac 1 $mono_file");
        $outputSTM = shell_exec($commandSTM);

        $commandRun = escapeshellcmd("analyze.py $target_name");
        $outputRun = shell_exec($commandRun);
        echo $outputRun;
        echo '</div><img src="icon.ico" width="150" height="150" style="position: absolute; top: 10%; left: 5%; transform: translate(-50%, -50%);"><script>hideLoading();</script>';
    } else {
        echo "Sorry, there was an error uploading your file.";
        echo '</div><img src="icon.ico" width="150" height="150" style="position: absolute; top: 10%; left: 5%; transform: translate(-50%, -50%);"><script>hideLoading();</script>';
        echo '<script>hideLoading();</script>';
    }
}
?>