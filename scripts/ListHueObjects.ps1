# ListHueRaw.ps1
$bridge = "192.168.1.56"
$user = "ronPYtO6-LY-nJuhcFuEvYi1oTB0VR5kPzPMuQnH"

# Hae raaka JSON ilman PowerShellin automaattista muunnosta
$response = Invoke-WebRequest -Uri "http://$bridge/api/$user/sensors" -UseBasicParsing

# Tulosta täsmälleen se mitä Hue Bridge palauttaa
$response.Content
