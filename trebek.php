<?php 
    
    $file = fopen('outgoing-hooks', "a");
    
    /*
        team_id=T0001
        channel_id=C2147483705
        channel_name=test
        timestamp=1355517523.000005
        user_id=U2147483697
        user_name=Steve
        text=googlebot: What is the air-speed velocity of an unladen swallow?
        trigger_word=googlebot:
    */

    $team_id = $_POST["team_id"];
    $channel_id = $_POST["channel_id"];
    $channel_name = $_POST["channel_name"];
    $timestamp = $_POST["timestamp"];
    $username = $_POST["user_name"];
    $text = $_POST["text"];
    
    $txt = "[" . $username . "] " . $text . "\n";


   fwrite($file, $txt);
   fclose($file);

?>
