import QtQuick 2.6
import QtQuick.Controls 2.1

Rectangle {
    id: mainWindow

    width: 750
    height: 500
    property alias comboBox: comboBox
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
        id: rectangle
        x: 0
        width: 200
        height: 200
        color: "#ffffff"
        opacity: 0

        Row {
            id: row1
            anchors.fill: parent
            opacity: 0




            Column {
                id: column3
                width: 200
                height: 400
                opacity: 0
            }
            Column {
                id: column
                width: 200
                height: 400
                opacity: 0

                Row {
                    id: row2
                    width: 200
                    height: 400
                    opacity: 0

                    Image {
                        id: image
                        width: 100
                        height: 100
                        opacity: 0
                        source: "img/bloodytools_icon.png"
                    }

                    Text {
                        id: text1
                        text: qsTr("Text")
                        opacity: 0
                        font.pixelSize: 12
                    }
                }
            }
            Column {
                id: column1
                width: 200
                height: 400
                opacity: 0

                Row {
                    id: row3
                    width: 200
                    height: 400
                    opacity: 0

                    Text {
                        id: text6
                        text: qsTr("Text")
                        opacity: 0
                        font.pixelSize: 12
                    }
                }
            }
            Column {
                id: column2
                width: 200
                height: 400
                opacity: 0

                Row {
                    id: row4
                    width: 200
                    height: 400
                    opacity: 0

                    Image {
                        id: image1
                        width: 100
                        height: 100
                        opacity: 0
                        source: "img/bloodytools_icon.png"
                    }

                    Text {
                        id: text7
                        text: qsTr("Text")
                        opacity: 0
                        font.pixelSize: 12
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
                target: settings_area
                x: 20
                y: 80
                width: 710
                height: 350
                clip: true
                opacity: 1
            }

            PropertyChanges {
                target: example_settings_group
                height: 30
                text: qsTr("How to treat a lady")
                font.bold: true
                font.pixelSize: 22
                opacity: 1
            }

            PropertyChanges {
                target: example_settings_group_organizer
                width: 710
                height: 100
                opacity: 1
            }

            PropertyChanges {
                target: example_settings_group_left_column
                width: 355
                opacity: 1
            }

            PropertyChanges {
                target: example_settings_group_right_column
                width: 355
                opacity: 1
            }

            PropertyChanges {
                target: example_settings_group_first_setting
                height: 50
                opacity: 1
            }

            PropertyChanges {
                target: example_settings_group_second_setting
                height: 50
                opacity: 1
            }

            PropertyChanges {
                target: text2
                width: 150
                height: 40
                text: qsTr("Hug her")
                verticalAlignment: Text.AlignVCenter
                font.pixelSize: 18
                opacity: 1
            }

            PropertyChanges {
                target: text3
                width: 150
                height: 40
                text: qsTr("Special action")
                font.pixelSize: 18
                verticalAlignment: Text.AlignVCenter
                opacity: 1
            }

            PropertyChanges {
                target: checkBox
                text: qsTr(" ")
                opacity: 1
            }

            PropertyChanges {
                target: comboBox
                width: 200
                clip: false
                currentIndex: 0
                opacity: 1
                model: [ "Kiss her neck", "Caress her back", "Bite her ear" ]
                font.pixelSize: 18
            }

            PropertyChanges {
                target: example_settings_group_third_setting
                height: 50
                spacing: 0
                opacity: 1
            }

            PropertyChanges {
                target: example_settings_group_fourth_setting
                height: 50
                opacity: 1
            }

            PropertyChanges {
                target: text4
                width: 150
                height: 40
                text: qsTr("Bug her")
                verticalAlignment: Text.AlignVCenter
                font.pixelSize: 18
                opacity: 1
            }

            PropertyChanges {
                target: text5
                width: 150
                height: 40
                text: qsTr("Know her name")
                font.pixelSize: 18
                verticalAlignment: Text.AlignVCenter
                opacity: 1
            }

            PropertyChanges {
                target: slider
                stepSize: 1
                to: 7
                value: 2
                scale: 0.8
                opacity: 1
            }

            PropertyChanges {
                target: textField
                text: qsTr("Insert her Name here")
                font.pixelSize: 18
                opacity: 1
            }

            PropertyChanges {
                target: row
                width: 710
                height: 30
                anchors.rightMargin: 510
                anchors.leftMargin: 0
                opacity: 1
            }

            PropertyChanges {
                target: rectangle
                x: -4
                y: -6
                width: 758
                height: 50
                radius: 7
                clip: true
                border.width: 2
                anchors.topMargin: -9
                anchors.bottomMargin: 446
                opacity: 1
            }

            PropertyChanges {
                target: row1
                spacing: 5
                opacity: 1
            }

            PropertyChanges {
                target: image
                x: 2
                y: 7
                width: 35
                height: 35
                fillMode: Image.PreserveAspectFit
                source: "img/bloodytools_icon.png"
                opacity: 1
            }

            PropertyChanges {
                target: text1
                y: 13
                text: qsTr("Bloodytools")
                font.bold: true
                verticalAlignment: Text.AlignVCenter
                font.pixelSize: 18
                opacity: 1
            }

            PropertyChanges {
                target: column
                width: 145
                height: 50
                clip: true
                spacing: 0
                opacity: 1
            }

            PropertyChanges {
                target: row2
                width: 155
                height: 50
                spacing: 5
                opacity: 1
            }

            PropertyChanges {
                target: column1
                width: 15
                height: 50
                opacity: 1
            }

            PropertyChanges {
                target: text6
                y: 11
                text: qsTr(">")
                font.bold: true
                font.pixelSize: 20
                opacity: 1
            }

            PropertyChanges {
                target: row3
                opacity: 1
            }

            PropertyChanges {
                target: column2
                width: 165
                height: 50
                spacing: 0
                clip: true
                opacity: 1
            }

            PropertyChanges {
                target: row4
                spacing: 5
                opacity: 1
            }

            PropertyChanges {
                target: image1
                y: 7
                width: 35
                height: 35
                fillMode: Image.PreserveAspectFit
                source: "img/repair-tools-cross.svg"
                opacity: 1
            }

            PropertyChanges {
                target: text7
                y: 13
                text: qsTr("Bloodystats")
                font.bold: true
                font.pixelSize: 18
                opacity: 1
            }

            PropertyChanges {
                target: column3
                width: 14
                height: 50
                opacity: 1
            }

            PropertyChanges {
                target: row5
                x: 20
                y: 440
                width: 710
                height: 40
                opacity: 1
            }

            PropertyChanges {
                target: item1
                width: 315
                height: 40
                opacity: 1
            }

            PropertyChanges {
                target: item2
                width: 35
                height: 40
                opacity: 1
            }

            PropertyChanges {
                target: rectangle1
                width: 150
                height: 40
                radius: 7
                border.width: 2
                opacity: 1
            }

            PropertyChanges {
                target: rectangle2
                width: 210
                height: 40
                radius: 7
                border.width: 2
                opacity: 1
            }

            PropertyChanges {
                target: text8
                text: qsTr("Simulate")
                font.pixelSize: 18
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                opacity: 1
            }

            PropertyChanges {
                target: text9
                width: 15
                text: qsTr("Save & Simulate")
                font.pixelSize: 18
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                opacity: 1
            }

            PropertyChanges {
                target: row6
                width: 710
                height: 30
                opacity: 1
            }

            PropertyChanges {
                target: row7
                width: 710
                height: 200
                opacity: 1
            }

            PropertyChanges {
                target: text10
                height: 30
                text: qsTr("Peters preferences")
                font.bold: true
                font.pixelSize: 22
                opacity: 1
            }

            PropertyChanges {
                target: column4
                width: 355
                height: 200
                opacity: 1
            }

            PropertyChanges {
                target: column5
                width: 355
                height: 200
                opacity: 1
            }

            PropertyChanges {
                target: row8
                height: 50
                opacity: 1
            }

            PropertyChanges {
                target: row9
                height: 50
                opacity: 1
            }

            PropertyChanges {
                target: row10
                height: 50
                opacity: 1
            }

            PropertyChanges {
                target: row11
                height: 50
                opacity: 1
            }

            PropertyChanges {
                target: text11
                width: 150
                height: 40
                text: qsTr("Food")
                verticalAlignment: Text.AlignVCenter
                font.pixelSize: 18
                opacity: 1
            }

            PropertyChanges {
                target: text12
                width: 150
                height: 40
                text: qsTr("Freetime")
                font.pixelSize: 18
                verticalAlignment: Text.AlignVCenter
                opacity: 1
            }

            PropertyChanges {
                target: text13
                width: 150
                height: 40
                text: qsTr("Loves")
                font.pixelSize: 18
                verticalAlignment: Text.AlignVCenter
                opacity: 1
            }

            PropertyChanges {
                target: text14
                width: 150
                height: 40
                text: qsTr("Special Care")
                font.pixelSize: 18
                verticalAlignment: Text.AlignVCenter
                opacity: 1
            }

            PropertyChanges {
                target: busyIndicator
                height: 40
                opacity: 1
            }

            PropertyChanges {
                target: progressBar
                height: 40
                scale: 1
                value: 0.7
                opacity: 1
            }

            PropertyChanges {
                target: switch1
                text: qsTr("off")
                opacity: 1
            }

            PropertyChanges {
                target: comboBox1
                width: 200
                model: [ "Bikinis", "Boobs", "Pizza", "Beeeeewbs" ]
                font.pixelSize: 18
                opacity: 1
            }
        }
    ]
    Column {
        id: settings_area
        width: 200
        height: 400
        opacity: 0


        Row {
            id: row
            width: 200
            height: 400
            opacity: 0

            Text {
                id: example_settings_group
                text: qsTr("Text")
                opacity: 0
                font.pixelSize: 12
            }
        }
        Row {
            id: example_settings_group_organizer
            width: 200
            height: 400
            opacity: 0

            Column {
                id: example_settings_group_left_column
                width: 200
                height: 400
                opacity: 0

                Row {
                    id: example_settings_group_first_setting
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
                    id: example_settings_group_third_setting
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
                id: example_settings_group_right_column
                width: 200
                height: 400
                opacity: 0

                Row {
                    id: example_settings_group_second_setting
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
                    id: example_settings_group_fourth_setting
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

        Row {
            id: row6
            width: 200
            height: 400
            opacity: 0

            Text {
                id: text10
                text: qsTr("Text")
                opacity: 0
                font.pixelSize: 12
            }
        }

        Row {
            id: row7
            width: 200
            height: 400
            opacity: 0

            Column {
                id: column4
                width: 200
                height: 400
                opacity: 0

                Row {
                    id: row8
                    width: 200
                    height: 400
                    opacity: 0

                    Text {
                        id: text11
                        text: qsTr("Text")
                        opacity: 0
                        font.pixelSize: 12
                    }

                    ProgressBar {
                        id: progressBar
                        opacity: 0
                        value: 0.5
                    }
                }

                Row {
                    id: row9
                    width: 200
                    height: 400
                    opacity: 0

                    Text {
                        id: text12
                        text: qsTr("Text")
                        opacity: 0
                        font.pixelSize: 12
                    }

                    Switch {
                        id: switch1
                        text: qsTr("Switch")
                        opacity: 0
                    }
                }
            }

            Column {
                id: column5
                width: 200
                height: 400
                opacity: 0

                Row {
                    id: row10
                    width: 200
                    height: 400
                    opacity: 0

                    Text {
                        id: text14
                        text: qsTr("Text")
                        opacity: 0
                        font.pixelSize: 12
                    }

                    BusyIndicator {
                        id: busyIndicator
                        opacity: 0
                    }
                }

                Row {
                    id: row11
                    width: 200
                    height: 400
                    opacity: 0

                    Text {
                        id: text13
                        text: qsTr("Text")
                        opacity: 0
                        font.pixelSize: 12
                    }

                    ComboBox {
                        id: comboBox1
                        opacity: 0
                    }
                }
            }
        }
    }

    Row {
        id: row5
        width: 200
        height: 400
        opacity: 0

        Item {
            id: item1
            width: 200
            height: 200
            opacity: 0
        }



        Rectangle {
            id: rectangle1
            width: 200
            height: 200
            color: "#ffffff"
            opacity: 0

            Text {
                id: text8
                text: qsTr("Text")
                anchors.fill: parent
                opacity: 0
                font.pixelSize: 12
            }
        }
        Item {
            id: item2
            width: 200
            height: 200
            opacity: 0
        }

        Rectangle {
            id: rectangle2
            width: 200
            height: 200
            color: "#ffffff"
            opacity: 0

            Text {
                id: text9
                text: qsTr("Text")
                anchors.fill: parent
                opacity: 0
                font.pixelSize: 12
            }
        }
    }
}
