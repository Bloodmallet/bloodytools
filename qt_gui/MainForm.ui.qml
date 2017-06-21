import QtQuick 2.6
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.1

Rectangle {
    id: mainWindow

    width: 750
    height: 500
    property alias mainWindow: mainWindow
    property alias bloodystatsIcon_i: bloodystatsIcon_i
    property alias switchToBloodystatsFakeButton_m: switchToBloodystatsFakeButton_m
    property alias switchToBloodytrinketsFakeButton_m: switchToBloodytrinketsFakeButton_m
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
            font.letterSpacing: 3
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
                    onClicked: mainWindow.state == "" ? mainWindow.state = "settings_bloodystats" : mainWindow.state = ""

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

            Rectangle {
                id: switchToBloodytrinkets_r
                x: -7
                y: 6
                color: "#ffffff"
                radius: 7
                border.width: 2
                anchors.bottomMargin: 20
                anchors.bottom: parent.bottom
                anchors.top: parent.top
                anchors.topMargin: 20
                anchors.leftMargin: 20
                MouseArea {
                    id: switchToBloodytrinketsFakeButton_m
                    anchors.fill: parent
                    Image {
                        id: bloodytrinketsIcon_i
                        x: 0
                        y: 0
                        width: 0
                        height: 0
                        clip: false
                        anchors.right: parent.right
                        opacity: 1
                        anchors.leftMargin: 100
                        fillMode: Image.PreserveAspectFit
                        anchors.bottom: bloodytrinketsTitle_t.top
                        anchors.bottomMargin: 0
                        source: "img/horizontal-bars-chart.svg"
                        anchors.left: parent.left
                        anchors.top: parent.top
                        visible: true
                        anchors.topMargin: 50
                        anchors.rightMargin: 100
                        z: 1
                    }

                    Text {
                        id: bloodytrinketsTitle_t
                        x: 40
                        y: 240
                        height: 50
                        text: qsTr("Bloodytrinkets")
                        verticalAlignment: Text.AlignVCenter
                        fontSizeMode: Text.Fit
                        transformOrigin: Item.Center
                        anchors.bottomMargin: 70
                        horizontalAlignment: Text.AlignHCenter
                        anchors.bottom: parent.bottom
                        anchors.leftMargin: 50
                        font.pixelSize: 30
                        anchors.right: parent.right
                        anchors.left: parent.left
                        anchors.rightMargin: 50
                    }
                }
                anchors.right: parent.right
                anchors.left: parent.horizontalCenter
                anchors.rightMargin: 20
            }
        }
    }

    Rectangle {
        id: top_menu_background
        height: 200
        color: "#ffffff"
        anchors.fill: parent
        opacity: 0

        RowLayout {
            id: top_menu_rowLayout
            anchors.fill: parent
            opacity: 0

            Column {
                id: column_left
                width: 200
                height: 400
                opacity: 0

                RowLayout {
                    id: top_left_menu_rowLayout
                    anchors.fill: parent
                    opacity: 0

                    Column {
                        id: column1
                        width: 200
                        height: 400
                        opacity: 0

                        MouseArea {
                            id: top_menu_tools_mouseArea
                            anchors.fill: parent
                            opacity: 0

                            Image {
                                id: bloodytools_image
                                x: 0
                                y: 0
                                width: 100
                                height: 100
                                opacity: 0
                                source: "img/tools.svg"
                                anchors.bottom: parent.bottom
                                anchors.leftMargin: 20
                                anchors.right: top_menu_tools_text.left
                                anchors.left: parent.left
                            }
                            Text {
                                id: top_menu_tools_text
                                text: qsTr("Text")
                                font.pixelSize: 12
                                opacity: 0
                                verticalAlignment: Text.AlignVCenter
                                fontSizeMode: Text.Fit
                                transformOrigin: Item.Center
                                horizontalAlignment: Text.AlignHCenter
                                anchors.bottom: parent.bottom
                                anchors.leftMargin: 100
                                anchors.right: parent.right
                                anchors.left: parent.left
                                anchors.rightMargin: 50
                            }
                        }
                    }

                    Column {
                        id: column2
                        width: 200
                        height: 400
                        opacity: 0
                    }
                }
            }

            Column {
                id: column_right
                width: 200
                height: 400
                opacity: 0
            }
        }
    }

    Column {
        id: column
        width: 200
        height: 400
        opacity: 0

        Text {
            id: text1
            text: qsTr("Text")
            opacity: 0
            font.pixelSize: 12
        }

        Row {
            id: row
            width: 200
            height: 400
            opacity: 0

            Column {
                id: column3
                width: 200
                height: 400
                opacity: 0

                Row {
                    id: row1
                    width: 200
                    height: 400
                    opacity: 0

                    Text {
                        id: text2
                        text: qsTr("Text")
                        opacity: 0
                        font.pixelSize: 12
                    }

                    CheckBox {
                        id: checkBox
                        text: qsTr("Check Box")
                        opacity: 0
                    }
                }

                Row {
                    id: row3
                    width: 200
                    height: 400
                    opacity: 0

                    Text {
                        id: text4
                        text: qsTr("Text")
                        opacity: 0
                        font.pixelSize: 12
                    }

                    Slider {
                        id: slider
                        opacity: 0
                        value: 0.5
                    }
                }
            }

            Column {
                id: column4
                width: 200
                height: 400
                opacity: 0

                Row {
                    id: row2
                    width: 200
                    height: 400
                    opacity: 0

                    Text {
                        id: text3
                        text: qsTr("Text")
                        opacity: 0
                        font.pixelSize: 12
                    }

                    ComboBox {
                        id: comboBox
                        opacity: 0
                    }
                }

                Row {
                    id: row4
                    width: 200
                    height: 400
                    opacity: 0

                    Text {
                        id: text5
                        text: qsTr("Text")
                        opacity: 0
                        font.pixelSize: 12
                    }

                    TextField {
                        id: textField
                        text: qsTr("Text Field")
                        opacity: 0
                    }
                }
            }
        }
    }
    states: [
        State {
            name: "settings_bloodystats"

            PropertyChanges {
                target: mainStateSwitch_r
                visible: false
            }

            PropertyChanges {
                target: programmTitle_t
                visible: false
                font.letterSpacing: 3
                horizontalAlignment: Text.AlignHCenter
            }

            PropertyChanges {
                target: top_menu_background
                height: 50
                radius: 1
                anchors.bottomMargin: 449
                anchors.rightMargin: 0
                anchors.leftMargin: 0
                anchors.topMargin: -6
                border.width: 2
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_rowLayout
                width: 750
                height: 48
                anchors.bottomMargin: 0
                opacity: 1
            }

            PropertyChanges {
                target: column_left
                height: 100
                Layout.minimumHeight: 40
                Layout.minimumWidth: 350
                spacing: 0
                Layout.fillHeight: true
                opacity: 1
            }

            PropertyChanges {
                target: column_right
                Layout.minimumHeight: 40
                Layout.minimumWidth: 320
                spacing: 0
                Layout.fillHeight: true
                opacity: 1
            }

            PropertyChanges {
                target: top_left_menu_rowLayout
                anchors.rightMargin: 0
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_tools_mouseArea
                anchors.bottomMargin: 0
                anchors.topMargin: 0
                hoverEnabled: true
                Layout.fillWidth: false
                Layout.fillHeight: true
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_tools_text
                x: 8
                y: 0
                width: 71
                text: qsTr("Bloodytools")
                anchors.leftMargin: 8
                anchors.rightMargin: 101
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                anchors.bottomMargin: 43
                anchors.topMargin: 0
                opacity: 1
            }

            PropertyChanges {
                target: column1
                Layout.minimumWidth: 180
                spacing: 0
                Layout.fillHeight: true
                opacity: 1
            }

            PropertyChanges {
                target: column2
                Layout.fillHeight: true
                opacity: 1
            }

            PropertyChanges {
                target: bloodytools_image
                anchors.leftMargin: 0
                anchors.bottomMargin: 5
                anchors.topMargin: 5
                fillMode: Image.PreserveAspectFit
                source: "img/bloodytols_icon.png"
                anchors.rightMargin: 0
                opacity: 1
            }

            PropertyChanges {
                target: column
                opacity: 1
            }

            PropertyChanges {
                target: text1
                opacity: 1
            }

            PropertyChanges {
                target: row
                opacity: 1
            }

            PropertyChanges {
                target: column3
                opacity: 1
            }

            PropertyChanges {
                target: column4
                opacity: 1
            }

            PropertyChanges {
                target: row1
                opacity: 1
            }

            PropertyChanges {
                target: row2
                opacity: 1
            }

            PropertyChanges {
                target: text2
                opacity: 1
            }

            PropertyChanges {
                target: text3
                opacity: 1
            }

            PropertyChanges {
                target: checkBox
                opacity: 1
            }

            PropertyChanges {
                target: comboBox
                opacity: 1
            }

            PropertyChanges {
                target: row3
                opacity: 1
            }

            PropertyChanges {
                target: row4
                opacity: 1
            }

            PropertyChanges {
                target: text4
                opacity: 1
            }

            PropertyChanges {
                target: text5
                opacity: 1
            }

            PropertyChanges {
                target: slider
                opacity: 1
            }

            PropertyChanges {
                target: textField
                opacity: 1
            }
        }
    ]
}
