# Carpcatcher Control 1.1.0 — eerste ontwikkelversie

Deze broncode is gebaseerd op KoggerApp 1.0.3 en gebruikt een eigen Android-identiteit:

- appnaam: `Carpcatcher Control`
- Android package: `nl.carpcatcher.control`
- sonar: TCP `10.42.1.1:5001`
- camera: RTSP `rtsp://10.42.1.1:8554/camera`
- Pixhawk: USB-serieel, normaal `57600 baud`

## In deze versie

- compact Carpcatcher-paneel in het hoofdscherm;
- knoppen om de vooraf ingevulde sonar- en cameraverbinding aan te maken;
- echogram-weergavesnelheid 1×, 2× of 3× zonder sonarmetingen weg te gooien;
- actuele Pixhawk-modus en accuspanning in het paneel;
- MAVLink `SET_MODE` voor Rover: MANUAL (0), HOLD (4), AUTO (10), RTL (11);
- RTL vereist ingedrukt houden;
- bediening is uitgeschakeld wanneer geen Pixhawk-heartbeat ontvangen wordt.
- de bestaande automatische waypointfunctie via de linkerstick blijft volledig behouden;
- opgeslagen waypoints, selectie op de kaart en MAVLink-missie-upload blijven behouden.

De huidige linkersticklogica gebruikt RC-kanaal 3, activeert boven 1800 PWM en wordt
na terugkeer onder 1600 PWM opnieuw vrijgegeven. Daarmee ontstaat maximaal één waypoint
per bewuste stickbeweging.

## Bouwen

Gebruik Qt 6.8.x met de Android SDK/NDK-configuratie die bij Qt hoort. De oorspronkelijke projectvereisten blijven gelden. Installeer deze build naast de originele KoggerApp; instellingen en pakketnaam zijn gescheiden.

Deze werkomgeving bevatte geen `cmake` of Qt Android toolchain. De wijzigingen zijn daarom statisch gecontroleerd, maar hier niet tot APK gecompileerd.
