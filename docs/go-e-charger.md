# go-e-laturin latausohjaus

Laturi liitetään Home Assistantiin HACS-integraatiolla `go-e APIv2 Connect`
(`marq24/ha-goecharger-api2`). Ota ensin go-e-sovelluksessa paikallinen HTTP API v2
käyttöön ja lisää integraatio Home Assistantiin laturin lähiverkko-osoitteella.
Valitse Home Assistant -versioon sopiva integraatiojulkaisu.

Dashboardin `[home_assistant]`-asetuksen `eqe_charging_switch_entity` arvoksi
asetetaan integraation `select.goe_<laitetunnus>_frc`. Dashboard lähettää
Home Assistantin `select.select_option`-kutsulla arvon `2` (käynnistä) tai `1`
(pysäytä). Arvo `0` tarkoittaa laturin automaattista ohjausta, jolloin
dashboard ei tulkitse ohjaustilaa päällä- tai pois-tilaksi. Käynnistyskomento
asettaa pakotetun latauksen; automaattiseen ohjaukseen voi palata valitsemalla
Home Assistantissa force state -arvoksi `0`.

Latausteho voidaan lukea laturilta asettamalla `eqe_charging_power_entity`
arvoksi `sensor.goe_<laitetunnus>_nrg_11` (kokonaisteho watteina).
Auton lataustilan, akun ja toimintamatkan nykyiset Mercedes-kohteet säilyvät.
Myös aiemmat `switch`- ja `light`-ohjauskohteet toimivat edelleen.

Lähteet: [integraatio](https://github.com/marq24/ha-goecharger-api2) ja
[valmistajan API-avaimet](https://github.com/goecharger/go-eCharger-API-v2/blob/main/API_KEYS_FIRMWARE/apikeys-en.md).
