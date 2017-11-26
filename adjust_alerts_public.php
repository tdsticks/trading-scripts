#!/usr/bin/php
//public domain
<?php

$apikey = "your-coinigy-api-key-here";
$apisecret = "your-coinigy-secret-here";
if($apikey == "your-coinigy-api-key-here") die("You have to put your coinigy api key and secret in the file\n");
######
$pct_new_price = 0.90; 
#what fraction you want your prices changed to. 
#below 1 lowers prices, above 1 raises them. 
#For example 0.90 will change your alerts to 90% of their original values


#get alerts
$ch = curl_init();

curl_setopt($ch, CURLOPT_URL, "https://api.coinigy.com/api/v1/alerts");
curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);
curl_setopt($ch, CURLOPT_HEADER, FALSE);
curl_setopt($ch, CURLOPT_POST, TRUE);
curl_setopt($ch, CURLOPT_HTTPHEADER, array("Content-Type: application/json", "Content-Length: 0", "X-API-KEY: $apikey", "X-API-SECRET: $apisecret"));
$response = curl_exec($ch);
curl_close($ch);
#var_dump($response);
$s = json_decode($response, TRUE);


foreach($s['data']['open_alerts'] as $x) {
    if($x["operator"] == ">") continue; #this ignores alerts above the current price since those don't need to be lowered
    $alert_id = $x["alert_id"];
    $mkt_name = $x["mkt_name"];
    $price = $x["price"];
    $exch_code = $x["exch_code"];
    echo "\n" . $mkt_name . "\n" . $exch_code . "\nOLD PRICE: $price * $pct_new_price\n";
    $price *= $pct_new_price;
    echo "NEW PRICE: $price\n\n";



    #delete alert
    echo "Press enter to continue change alert for $mkt_name. Comment this out in the file when you're satisfied everything works correctly"; fgets(fopen("php://stdin", "r"));
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, "https://api.coinigy.com/api/v1/deleteAlert");
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);
    curl_setopt($ch, CURLOPT_HEADER, FALSE);
    curl_setopt($ch, CURLOPT_POST, TRUE);

    curl_setopt($ch, CURLOPT_POSTFIELDS, "{ \"alert_id\": $alert_id }");
    curl_setopt($ch, CURLOPT_HTTPHEADER, array( "Content-Type: application/json", "X-API-KEY: $apikey", "X-API-SECRET: $apisecret" ));

    $response = curl_exec($ch);
    curl_close($ch);
    var_dump($response);


    #add alert
    #fgets(fopen("php://stdin", "r"));
    $ch = curl_init();

    curl_setopt($ch, CURLOPT_URL, "https://api.coinigy.com/api/v1/addAlert");
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);
    curl_setopt($ch, CURLOPT_HEADER, FALSE);

    curl_setopt($ch, CURLOPT_POST, TRUE);

    curl_setopt ($ch, CURLOPT_POSTFIELDS, "{\"exch_code\": \"$exch_code\",\"market_name\": \"$mkt_name\",\"alert_price\": $price, \"alert_note\": \"\" }");

    curl_setopt($ch, CURLOPT_HTTPHEADER, array(
    "Content-Type: application/json",
    "X-API-KEY: $apikey",
    "X-API-SECRET: $apisecret"
    ));

    $response = curl_exec($ch);
    curl_close($ch);

    var_dump($response);
    sleep(5); #this is so we don't hit coinigy with too many api calls too quickly
}
