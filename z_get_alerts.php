#!/usr/bin/php
<?php

#To make this work, you have to add your coinigy api key and secret in the line with CURLOPT_HTTPHEADER in it

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, "https://api.coinigy.com/api/v1/alerts");
curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);
#curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);
curl_setopt($ch, CURLOPT_HEADER, FALSE);
curl_setopt($ch, CURLOPT_POST, TRUE);
curl_setopt($ch, CURLOPT_HTTPHEADER, array("Content-Type: application/json", "Content-Length: 0", "X-API-KEY: your--api--key--here", "X-API-SECRET: your---api---secret---here"));
$response = curl_exec($ch);
curl_close($ch);
#var_dump($response);
$s = json_decode($response, TRUE);
file_put_contents("alerts.txt", "");
foreach($s['data']['open_alerts'] as $x){
    $y = explode("/", $x["mkt_name"]);
    $y = array($y[1], $y[0]);
    $y = implode("-", $y);
    #echo $x["mkt_name"] . " " . $x["operator"] . " " . $x["price"] . " \n";
    file_put_contents("alerts.txt", $y . " " . $x["operator"] . " " . $x["price"] . "\n", FILE_APPEND);
    #echo $y . " " . $x["operator"] . " " . $x["price"] . " \n";
    }
