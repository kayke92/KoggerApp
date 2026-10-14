import QtQuick 2.15
import QtQuick.Controls 2.15
import QtCore
import kqml_types 1.0

Rectangle {
    id: root
    property int sonarSpeed: prefs.sonarSpeed
    property int activeMode: deviceManagerWrapper ? deviceManagerWrapper.pilotModeState : -1
    property real voltage: deviceManagerWrapper ? deviceManagerWrapper.vruVoltage : NaN
    property real velocity: deviceManagerWrapper ? deviceManagerWrapper.vruVelocityH : NaN
    property bool telemetryAvailable: activeMode >= 0
    signal sonarSpeedRequested(int speed)
    signal modeRequested(string mode)
    signal connectSonarRequested()
    signal connectCameraRequested()

    width: Math.min(parent ? parent.width - 16 : 720, 760)
    height: 54
    radius: 10
    color: "#E61A202C"
    border.color: "#52627A"
    border.width: 1

    Settings {
        id: prefs
        category: "carpcatcher/control"
        property int sonarSpeed: 1
    }

    Row {
        anchors.fill: parent
        anchors.margins: 7
        spacing: 6

        Label {
            anchors.verticalCenter: parent.verticalCenter
            text: "CARPCATCHER"
            color: "#FF8A25"
            font.bold: true
        }

        Button { text: "SONAR"; onClicked: root.connectSonarRequested() }
        Button { text: "CAM"; onClicked: root.connectCameraRequested() }

        ComboBox {
            width: 92
            model: ["1×", "2×", "3×"]
            currentIndex: Math.max(0, prefs.sonarSpeed - 1)
            onActivated: {
                prefs.sonarSpeed = currentIndex + 1
                root.sonarSpeedRequested(prefs.sonarSpeed)
            }
            ToolTip.visible: hovered
            ToolTip.text: qsTr("Sonar image speed")
        }

        Repeater {
            model: ["MANUAL", "HOLD", "AUTO"]
            delegate: Button {
                required property string modelData
                text: modelData
                enabled: root.telemetryAvailable
                onClicked: root.modeRequested(modelData)
            }
        }

        Button {
            text: "RTL"
            enabled: root.telemetryAvailable
            highlighted: true
            onPressAndHold: root.modeRequested("RTL")
            ToolTip.visible: hovered
            ToolTip.text: qsTr("Press and hold for Return To Launch")
        }

        Label {
            anchors.verticalCenter: parent.verticalCenter
            text: root.telemetryAvailable
                  ? ("MODE " + root.activeMode + "   "
                     + (isNaN(root.voltage) ? "—" : root.voltage.toFixed(1) + " V"))
                  : qsTr("No telemetry")
            color: root.telemetryAvailable ? "#75E6A4" : "#FFBE5C"
        }
    }
}
