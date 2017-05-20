import QtQuick 2.6
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.3

Rectangle {
    id: mainWindow

    width: 750
    height: 500
    color: "#ffffff"
    property alias button: button

    property alias mouseArea1: mouseArea1
    property alias image: image
    property alias mouseArea: mouseArea
    border.color: "#000000"

    MouseArea {
        id: mouseArea
        anchors.rightMargin: 0
        anchors.bottomMargin: 0
        anchors.leftMargin: 0
        anchors.topMargin: 0
        anchors.fill: parent

        Text {
            id: programmTitle
            x: 272
            width: 206
            height: 46
            text: qsTr("Bloodytools")
            font.weight: Font.DemiBold
            anchors.top: parent.top
            anchors.topMargin: 20
            anchors.horizontalCenter: parent.horizontalCenter
            font.pixelSize: 34
            elide: Text.ElideNone
            topPadding: 0
            font.letterSpacing: 3
            font.wordSpacing: 0
            style: Text.Normal
            fontSizeMode: Text.VerticalFit
        }

        Rectangle {
            id: rectangle
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
                id: switchToBloodystats
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
                    id: mouseArea1
                    anchors.fill: parent

                    Image {
                        id: image
                        x: 0
                        y: 0
                        width: 36
                        height: 36
                        anchors.right: parent.right
                        anchors.rightMargin: 40
                        anchors.left: parent.left
                        anchors.leftMargin: 40
                        fillMode: Image.PreserveAspectFit
                        opacity: 1
                        clip: false
                        visible: true
                        z: 1
                        anchors.bottom: text1.top
                        anchors.top: parent.top
                        anchors.bottomMargin: 0
                        anchors.topMargin: 30
                        source: "img/repair-tools-cross.svg"
                    }

                    Text {
                        id: text1
                        x: 40
                        y: 240
                        height: 75
                        text: qsTr("Bloodystats")
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignHCenter
                        anchors.right: parent.right
                        anchors.rightMargin: 40
                        anchors.left: parent.left
                        anchors.leftMargin: 40
                        fontSizeMode: Text.Fit
                        transformOrigin: Item.Center
                        anchors.bottom: parent.bottom
                        anchors.bottomMargin: 50
                        font.pixelSize: 86
                    }
                }
            }

            Button {
                id: button
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
                    id: image1
                    y: 24
                    anchors.left: parent.left
                    anchors.leftMargin: 40
                    fillMode: Image.PreserveAspectFit
                    anchors.right: parent.right
                    anchors.rightMargin: 40
                    anchors.bottom: text2.top
                    anchors.bottomMargin: 0
                    anchors.top: parent.top
                    anchors.topMargin: 30
                    source: "img/horizontal-bars-chart.png"
                }

                Text {
                    id: text2
                    y: 234
                    height: 75
                    text: qsTr("Bloodytrinkets")
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    anchors.right: parent.right
                    anchors.rightMargin: 40
                    anchors.left: parent.left
                    anchors.leftMargin: 40
                    fontSizeMode: Text.Fit
                    padding: -3
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 50
                    font.pixelSize: 86
                }
            }
        }
    }

    Image {
        id: image2
        x: 49
        y: 18
        width: 100
        height: 100
        opacity: 0
        source: "qrc:/qtquickplugin/images/template_image.png"
    }
    states: [
        State {
            name: "bloodystats_settings"

            PropertyChanges {
                target: image2
                x: 8
                y: 8
                width: 57
                height: 40
                sourceSize.height: 0
                sourceSize.width: 0
                fillMode: Image.PreserveAspectFit
                source: "img/bloodytols_icon.png"
                opacity: 1
            }

            PropertyChanges {
                target: image1
                visible: false
            }

            PropertyChanges {
                target: programmTitle
                x: 67
                anchors.horizontalCenterOffset: -203
                anchors.topMargin: 8
            }

            PropertyChanges {
                target: button
                visible: false
            }

            PropertyChanges {
                target: switchToBloodystats
                visible: false
            }

            PropertyChanges {
                target: rectangle
                visible: false
            }
        },
        State {
            name: "bloodytrinkets_settings"
            PropertyChanges {
                target: image2
                x: 8
                y: 8
                width: 57
                height: 40
                opacity: 1
                sourceSize.width: 0
                sourceSize.height: 0
                fillMode: Image.PreserveAspectFit
                source: "img/bloodytols_icon.png"
            }

            PropertyChanges {
                target: image1
                visible: false
            }

            PropertyChanges {
                target: programmTitle
                x: 67
                anchors.horizontalCenterOffset: -203
                anchors.topMargin: 8
            }

            PropertyChanges {
                target: button
                visible: false
            }

            PropertyChanges {
                target: switchToBloodystats
                visible: false
            }

            PropertyChanges {
                target: rectangle
                visible: false
            }
        }
    ]
}
