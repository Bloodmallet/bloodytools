import QtQuick 2.6
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.3

Rectangle {
    id: mainWindow

    width: 750
    height: 500
    property alias switchToBloodytrinkets_b: switchToBloodytrinkets_b
    property alias bloodystatsIcon_i: bloodystatsIcon_i
    property alias switchToBloodystatsFakeButton_m: switchToBloodystatsFakeButton_m
    property alias rootArea_m: rootArea_m
    gradient: Gradient {
        GradientStop {
            position: 0.429
            color: "#ffffff"
        }

        GradientStop {
            position: 1
            color: "#505050"
        }
    }

    border.color: "#000000"

    MouseArea {
        id: rootArea_m
        anchors.rightMargin: 0
        anchors.bottomMargin: 0
        anchors.leftMargin: 0
        anchors.topMargin: 0
        anchors.fill: parent

        Text {
            id: programmTitle_t
            text: qsTr("Bloodytools")
            anchors.bottom: mainStateSwitch_r.top
            anchors.bottomMargin: 0
            anchors.right: parent.right
            anchors.rightMargin: 40
            anchors.left: parent.left
            anchors.leftMargin: 40
            horizontalAlignment: Text.AlignHCenter
            font.weight: Font.DemiBold
            anchors.top: parent.top
            anchors.topMargin: 20
            font.pixelSize: 120
            elide: Text.ElideNone
            topPadding: 0
            font.letterSpacing: 3
            font.wordSpacing: 0
            style: Text.Normal
            fontSizeMode: Text.Fit
        }

        Rectangle {
            id: mainStateSwitch_r
            color: "#00ffffff"
            border.width: 0
            anchors.right: parent.right
            anchors.rightMargin: 20
            anchors.left: parent.left
            anchors.leftMargin: 20
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 20
            anchors.top: parent.top
            anchors.topMargin: 80

            Rectangle {
                id: switchToBloodystats_r
                x: 0
                y: 0
                color: "#ffffff"
                radius: 7
                anchors.right: parent.horizontalCenter
                anchors.rightMargin: 20
                anchors.left: parent.left
                anchors.leftMargin: 20
                anchors.bottom: parent.bottom
                anchors.top: parent.top
                anchors.bottomMargin: 20
                anchors.topMargin: 20
                border.width: 2

                MouseArea {
                    id: switchToBloodystatsFakeButton_m
                    anchors.fill: parent

                    Image {
                        id: bloodystatsIcon_i
                        x: 0
                        y: 0
                        width: 0
                        height: 0
                        anchors.right: parent.right
                        anchors.rightMargin: 100
                        anchors.left: parent.left
                        anchors.leftMargin: 100
                        fillMode: Image.PreserveAspectFit
                        opacity: 1
                        clip: false
                        visible: true
                        z: 1
                        anchors.bottom: bloodystatsTitle_t.top
                        anchors.top: parent.top
                        anchors.bottomMargin: 0
                        anchors.topMargin: 50
                        source: "img/tools.svg"
                    }

                    Text {
                        id: bloodystatsTitle_t
                        x: 40
                        y: 240
                        height: 50
                        text: qsTr("Bloodystats")
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignHCenter
                        anchors.right: parent.right
                        anchors.rightMargin: 50
                        anchors.left: parent.left
                        anchors.leftMargin: 50
                        fontSizeMode: Text.Fit
                        transformOrigin: Item.Center
                        anchors.bottom: parent.bottom
                        anchors.bottomMargin: 70
                        font.pixelSize: 30
                    }
                }
            }

            Button {
                id: switchToBloodytrinkets_b
                x: 0
                y: 0
                width: 315
                text: qsTr("")
                anchors.right: parent.right
                anchors.rightMargin: 20
                anchors.left: parent.horizontalCenter
                anchors.leftMargin: 20
                anchors.bottom: parent.bottom
                anchors.top: parent.top
                visible: true
                autoRepeat: false
                autoExclusive: false
                checked: false
                checkable: false
                highlighted: false
                spacing: 0
                anchors.bottomMargin: 20
                anchors.topMargin: 20

                Image {
                    id: bloodytrinketsIcon_i
                    y: 24
                    width: 0
                    height: 0
                    anchors.left: parent.left
                    anchors.leftMargin: 100
                    fillMode: Image.PreserveAspectFit
                    anchors.right: parent.right
                    anchors.rightMargin: 100
                    anchors.bottom: bloodytrinketsTitle_t.top
                    anchors.bottomMargin: 0
                    anchors.top: parent.top
                    anchors.topMargin: 50
                    source: "img/horizontal-bars-chart.png"
                }

                Text {
                    id: bloodytrinketsTitle_t
                    y: 234
                    height: 50
                    text: qsTr("Bloodytrinkets")
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    anchors.right: parent.right
                    anchors.rightMargin: 50
                    anchors.left: parent.left
                    anchors.leftMargin: 50
                    fontSizeMode: Text.Fit
                    padding: -3
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 70
                    font.pixelSize: 30
                }
            }
        }
    }
    states: [
        State {
            name: "bloodystats_settings"

            PropertyChanges {
                target: bloodytrinketsIcon_i
                visible: false
            }

            PropertyChanges {
                target: programmTitle_t
                x: 67
                anchors.horizontalCenterOffset: -203
                anchors.topMargin: 8
            }

            PropertyChanges {
                target: switchToBloodytrinkets_b
                visible: false
            }

            PropertyChanges {
                target: switchToBloodystats_r
                visible: false
            }

            PropertyChanges {
                target: mainStateSwitch_r
                visible: false
            }
        },
        State {
            name: "bloodytrinkets_settings"

            PropertyChanges {
                target: bloodytrinketsIcon_i
                visible: false
            }

            PropertyChanges {
                target: programmTitle_t
                x: 67
                anchors.horizontalCenterOffset: -203
                anchors.topMargin: 8
            }

            PropertyChanges {
                target: switchToBloodytrinkets_b
                visible: false
            }

            PropertyChanges {
                target: switchToBloodystats_r
                visible: false
            }

            PropertyChanges {
                target: mainStateSwitch_r
                visible: false
            }
        }
    ]
}
