import QtQuick 2.6
import QtQuick.Controls 2.1

Rectangle {
    id: mainWindow

    width: 750
    height: 500
    property alias top_menu_profiler_profile_picker: top_menu_profiler_profile_picker
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
        id: top_menu_background
        x: 0
        width: 200
        height: 200
        color: "#ffffff"
        opacity: 0

        Row {
            id: top_menu_organizer
            anchors.fill: parent
            opacity: 0




            Column {
                id: top_menu_placeholder1
                width: 200
                height: 400
                opacity: 0
            }
            Column {
                id: top_menu_bloodytools_group
                width: 200
                height: 400
                opacity: 0

                Row {
                    id: top_menu_bloodytools_organizer
                    width: 200
                    height: 400
                    opacity: 0

                    Image {
                        id: top_menu_bloodytools_icon
                        width: 100
                        height: 100
                        opacity: 0
                        source: "img/bloodytools_icon.png"
                    }

                    Text {
                        id: top_menu_bloodytools_text
                        text: qsTr("Text")
                        opacity: 0
                        font.pixelSize: 12
                    }
                }
            }
            Column {
                id: top_menu_submenu_sign_group
                width: 200
                height: 400
                opacity: 0

                Row {
                    id: top_menu_submenu_organizer
                    width: 200
                    height: 400
                    opacity: 0

                    Text {
                        id: top_menu_submenu_sign
                        text: qsTr("Text")
                        opacity: 0
                        font.pixelSize: 12
                    }
                }
            }
            Column {
                id: top_menu_bloodystats_group
                width: 200
                height: 400
                opacity: 0

                Row {
                    id: top_menu_bloodystats_organizer
                    width: 200
                    height: 400
                    opacity: 0

                    Image {
                        id: top_menu_bloodystats_icon
                        width: 100
                        height: 100
                        opacity: 0
                        source: "img/bloodytools_icon.png"
                    }

                    Text {
                        id: top_menu_bloodystats_text
                        text: qsTr("Text")
                        opacity: 0
                        font.pixelSize: 12
                    }
                }
            }

            Column {
                id: top_menu_placeholder2
                width: 200
                height: 400
                opacity: 0
            }

            Column {
                id: top_menu_profiler_group
                width: 200
                height: 400
                opacity: 0

                Row {
                    id: top_menu_profiler_organizer
                    width: 200
                    height: 400
                    opacity: 0

                    ComboBox {
                        id: top_menu_profiler_profile_picker
                        opacity: 0
                    }

                    Image {
                        id: top_menu_profiles_settings
                        width: 100
                        height: 100
                        source: "img/settings.svg"
                        opacity: 0

                        MouseArea {
                            id: top_menu_settings_mousearea
                            anchors.fill: parent
                            opacity: 0
                            onClicked: mainWindow.state == "settings_bloodystats" ? mainWindow.state = "profiler_bloodystats" : mainWindow.state = "settings_bloodystats"
                        }
                    }
                }
            }
        }

        MouseArea {
            id: top_menu_bloodytools_mousearea
            x: 19
            y: 0
            width: 100
            height: 100
            opacity: 0
            onClicked: mainWindow.state = ""
        }

        MouseArea {
            id: top_menu_bloodystats_mousearea
            x: 18
            y: -2
            width: 100
            height: 100
            opacity: 0
            onClicked: mainWindow.state = "settings_bloodystats"
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
                x: 10
                y: 20
                width: 710
                height: 350
                clip: true
                opacity: 1
            }

            PropertyChanges {
                target: example_settings_group
                height: 30
                text: qsTr("General settings")
                font.weight: Font.DemiBold
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
                text: qsTr("PTR")
                verticalAlignment: Text.AlignVCenter
                font.pixelSize: 18
                opacity: 1
            }

            PropertyChanges {
                target: text3
                width: 150
                height: 40
                text: qsTr("Fight style")
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
                model: [ "Patchwerk", "HeavyMovement", "Beastlord" ]
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
                text: qsTr("Target error")
                verticalAlignment: Text.AlignVCenter
                font.pixelSize: 18
                opacity: 1
            }

            PropertyChanges {
                target: text5
                width: 150
                height: 40
                text: qsTr("Name of the run")
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
                text: qsTr("Insert name here")
                font.pixelSize: 18
                opacity: 1
            }

            PropertyChanges {
                target: row
                width: 710
                height: 30
                clip: true
                anchors.rightMargin: 510
                anchors.leftMargin: 0
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_background
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
                target: top_menu_organizer
                clip: true
                spacing: 5
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_bloodytools_icon
                x: 2
                y: 10
                width: 35
                height: 35
                fillMode: Image.PreserveAspectFit
                source: "img/bloodytools_icon.png"
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_bloodytools_text
                y: 18
                text: qsTr("Bloodytools")
                font.weight: Font.DemiBold
                font.bold: true
                verticalAlignment: Text.AlignVCenter
                font.pixelSize: 18
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_bloodytools_group
                width: 145
                height: 50
                clip: true
                spacing: 0
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_bloodytools_organizer
                width: 145
                height: 50
                spacing: 5
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_submenu_sign_group
                width: 15
                height: 50
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_submenu_sign
                y: 17
                text: qsTr(">")
                font.bold: true
                font.pixelSize: 20
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_submenu_organizer
                width: 15
                height: 50
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_bloodystats_group
                width: 165
                height: 50
                spacing: 0
                clip: true
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_bloodystats_organizer
                spacing: 5
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_bloodystats_icon
                y: 13
                width: 30
                height: 30
                fillMode: Image.PreserveAspectFit
                source: "img/tools.svg"
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_bloodystats_text
                y: 17
                text: qsTr("Bloodystats")
                font.weight: Font.DemiBold
                font.bold: true
                font.pixelSize: 18
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_placeholder1
                width: 14
                height: 50
                opacity: 1
            }

            PropertyChanges {
                target: bloodystats_settings_footer
                x: 20
                y: 440
                width: 710
                height: 40
                opacity: 1
            }

            PropertyChanges {
                target: bloodystats_settings_footer_placeholder1
                width: 315
                height: 40
                opacity: 1
            }

            PropertyChanges {
                target: bloodystats_settings_footer_placeholder2
                width: 35
                height: 40
                opacity: 1
            }

            PropertyChanges {
                target: bloodystats_settings_footer_simulate
                width: 150
                height: 40
                radius: 7
                border.width: 2
                opacity: 1
            }

            PropertyChanges {
                target: bloodystats_settings_footer_save_simulate
                width: 210
                height: 40
                radius: 7
                border.width: 2
                opacity: 1
            }

            PropertyChanges {
                target: bloodystats_settings_footer_simulate_text
                text: qsTr("Simulate")
                font.pixelSize: 18
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                opacity: 1
            }

            PropertyChanges {
                target: bloodystats_settings_footer_save_simulate_text
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
                height: 80
                clip: true
                opacity: 1
            }

            PropertyChanges {
                target: text10
                height: 30
                text: qsTr("Advanced settings")
                font.weight: Font.DemiBold
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
                text: qsTr("Upper bound")
                verticalAlignment: Text.AlignVCenter
                font.pixelSize: 18
                opacity: 1
            }

            PropertyChanges {
                target: text12
                width: 150
                height: 40
                text: qsTr("Default actions")
                font.pixelSize: 18
                verticalAlignment: Text.AlignVCenter
                opacity: 1
            }

            PropertyChanges {
                target: text13
                width: 150
                height: 40
                text: qsTr("Calculation method")
                font.pixelSize: 18
                verticalAlignment: Text.AlignVCenter
                opacity: 1
            }

            PropertyChanges {
                target: text14
                width: 150
                height: 40
                text: qsTr("Something loads")
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
                model: [ "Differential Evolution", "2fast" ]
                font.pixelSize: 18
                opacity: 1
            }

            PropertyChanges {
                target: settings_mainarea_bloodystats_background
                x: 10
                y: 60
                width: 730
                height: 370
                radius: 7
                border.width: 2
                opacity: 1
            }

            PropertyChanges {
                target: item3
                width: 248
                height: 30
                opacity: 1
            }

            PropertyChanges {
                target: item4
                width: 230
                height: 30
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_placeholder2
                width: 117
                height: 50
                clip: false
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_profiler_group
                width: 260
                height: 50
                clip: true
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_profiler_organizer
                width: 260
                height: 50
                spacing: 4
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_profiler_profile_picker
                x: 0
                y: 10
                width: 220
                height: 35
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_profiles_settings
                y: 10
                width: 35
                height: 35
                source: "img/settings.svg"
                opacity: 1
            }

            PropertyChanges {
                target: rootArea_m
                visible: false
            }

            PropertyChanges {
                target: top_menu_settings_mousearea
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_bloodytools_mousearea
                x: 14
                y: 0
                width: 153
                height: 50
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_bloodystats_mousearea
                x: 188
                y: 0
                width: 157
                height: 50
            }

            PropertyChanges {
                target: footer_simulate_mousearea
                x: 334
                y: 440
                width: 150
                height: 40
                opacity: 1
            }

            PropertyChanges {
                target: footer_simulate_save_mousearea
                x: 520
                y: 440
                width: 210
                height: 40
            }

            PropertyChanges {
                target: listView
                width: 350
                height: 110
                spacing: 2
                contentHeight: 40
                contentWidth: 350
                flickableDirection: Flickable.HorizontalAndVerticalFlick
                opacity: 1
            }
        },
        State {
            name: "profiler_bloodystats"
            PropertyChanges {
                target: mainStateSwitch_r
                visible: false
            }

            PropertyChanges {
                target: programmTitle_t
                horizontalAlignment: Text.AlignHCenter
                font.letterSpacing: 3
                visible: false
            }

            PropertyChanges {
                target: settings_area
                x: 10
                y: 20
                width: 710
                height: 350
                opacity: 1
                clip: true
            }

            PropertyChanges {
                target: example_settings_group
                height: 30
                text: qsTr("General settings")
                font.weight: Font.DemiBold
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
                text: qsTr("PTR")
                verticalAlignment: Text.AlignVCenter
                font.pixelSize: 18
                opacity: 1
            }

            PropertyChanges {
                target: text3
                width: 150
                height: 40
                text: qsTr("Fight style")
                verticalAlignment: Text.AlignVCenter
                font.pixelSize: 18
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
                currentIndex: 0
                font.pixelSize: 18
                model: [ "Patchwerk", "HeavyMovement", "Beastlord" ]
                opacity: 1
                clip: false
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
                text: qsTr("Target error")
                verticalAlignment: Text.AlignVCenter
                font.pixelSize: 18
                opacity: 1
            }

            PropertyChanges {
                target: text5
                width: 150
                height: 40
                text: qsTr("Name of the run")
                verticalAlignment: Text.AlignVCenter
                font.pixelSize: 18
                opacity: 1
            }

            PropertyChanges {
                target: slider
                value: 2
                to: 7
                scale: 0.8
                stepSize: 1
                opacity: 1
            }

            PropertyChanges {
                target: textField
                text: qsTr("Insert name here")
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
                clip: true
            }

            PropertyChanges {
                target: top_menu_background
                x: "-4"
                y: "-6"
                width: 758
                height: 50
                radius: 7
                anchors.bottomMargin: 446
                border.width: 2
                opacity: 1
                anchors.topMargin: "-9"
                clip: true
            }

            PropertyChanges {
                target: top_menu_organizer
                spacing: 5
                clip: true
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_bloodytools_icon
                x: 2
                y: 10
                width: 35
                height: 35
                source: "img/bloodytools_icon.png"
                fillMode: Image.PreserveAspectFit
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_bloodytools_text
                y: 18
                text: qsTr("Bloodytools")
                verticalAlignment: Text.AlignVCenter
                font.weight: Font.DemiBold
                font.bold: true
                font.pixelSize: 18
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_bloodytools_group
                width: 145
                height: 50
                spacing: 0
                opacity: 1
                clip: true
            }

            PropertyChanges {
                target: top_menu_bloodytools_organizer
                width: 145
                height: 50
                spacing: 5
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_submenu_sign_group
                width: 15
                height: 50
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_submenu_sign
                y: 17
                text: qsTr(">")
                font.bold: true
                font.pixelSize: 20
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_submenu_organizer
                height: 50
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_bloodystats_group
                width: 165
                height: 50
                spacing: 0
                opacity: 1
                clip: true
            }

            PropertyChanges {
                target: top_menu_bloodystats_organizer
                spacing: 5
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_bloodystats_icon
                y: 13
                width: 30
                height: 30
                source: "img/tools.svg"
                fillMode: Image.PreserveAspectFit
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_bloodystats_text
                y: 17
                text: qsTr("Bloodystats")
                font.weight: Font.DemiBold
                font.bold: true
                font.pixelSize: 18
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_placeholder1
                width: 14
                height: 50
                opacity: 1
            }

            PropertyChanges {
                target: bloodystats_settings_footer
                x: 20
                y: 440
                width: 710
                height: 40
                opacity: 1
            }

            PropertyChanges {
                target: bloodystats_settings_footer_placeholder1
                width: 315
                height: 40
                opacity: 1
            }

            PropertyChanges {
                target: bloodystats_settings_footer_placeholder2
                width: 35
                height: 40
                visible: false
                opacity: 1
            }

            PropertyChanges {
                target: bloodystats_settings_footer_simulate
                width: 150
                height: 40
                radius: 7
                visible: false
                border.width: 2
                opacity: 1
            }

            PropertyChanges {
                target: bloodystats_settings_footer_save_simulate
                width: 210
                height: 40
                radius: 7
                visible: false
                border.width: 2
                opacity: 1
            }

            PropertyChanges {
                target: bloodystats_settings_footer_simulate_text
                text: qsTr("Simulate")
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                font.pixelSize: 18
                opacity: 1
            }

            PropertyChanges {
                target: bloodystats_settings_footer_save_simulate_text
                width: 15
                text: qsTr("Save & Simulate")
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                font.pixelSize: 18
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
                text: qsTr("Advanced settings")
                font.weight: Font.DemiBold
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
                text: qsTr("Upper bound")
                verticalAlignment: Text.AlignVCenter
                font.pixelSize: 18
                opacity: 1
            }

            PropertyChanges {
                target: text12
                width: 150
                height: 40
                text: qsTr("Default actions")
                verticalAlignment: Text.AlignVCenter
                font.pixelSize: 18
                opacity: 1
            }

            PropertyChanges {
                target: text13
                width: 150
                height: 40
                text: qsTr("Calculation method")
                verticalAlignment: Text.AlignVCenter
                font.pixelSize: 18
                opacity: 1
            }

            PropertyChanges {
                target: text14
                width: 150
                height: 40
                text: qsTr("Something loads")
                verticalAlignment: Text.AlignVCenter
                font.pixelSize: 18
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
                value: 0.7
                scale: 1
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
                font.pixelSize: 18
                model: [ "Differential Evolution", "2fast" ]
                opacity: 1
            }

            PropertyChanges {
                target: settings_mainarea_bloodystats_background
                x: 10
                y: 60
                width: 730
                height: 370
                radius: 7
                visible: false
                border.width: 2
                opacity: 1
            }

            PropertyChanges {
                target: item3
                width: 248
                height: 30
                opacity: 1
            }

            PropertyChanges {
                target: item4
                width: 230
                height: 30
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_placeholder2
                width: 127
                height: 50
                visible: false
                clip: false
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_profiler_group
                width: 260
                height: 50
                visible: false
                clip: true
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_profiler_organizer
                width: 260
                height: 50
                spacing: 4
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_profiler_profile_picker
                x: 0
                y: 10
                width: 220
                height: 35
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_profiles_settings
                y: 10
                width: 35
                height: 35
                source: "img/settings.svg"
                opacity: 1
            }

            PropertyChanges {
                target: rootArea_m
                visible: false
            }

            PropertyChanges {
                target: bloodystats_settings_footer_profiler_save
                width: 150
                height: 40
                radius: 7
                border.width: 2
                opacity: 1
            }

            PropertyChanges {
                target: bloodystats_settings_footer_profiler_save_text
                text: qsTr("Save")
                font.pixelSize: 18
                font.weight: Font.DemiBold
                font.bold: true
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                opacity: 1
            }

            PropertyChanges {
                target: profiler_bloodystats_background
                x: 10
                y: 60
                width: 730
                height: 370
                opacity: 1
            }

            PropertyChanges {
                target: top_menu_bloodytools_mousearea
                width: 148
                height: 50
            }

            PropertyChanges {
                target: top_menu_bloodystats_mousearea
                x: 188
                y: 0
                width: 157
                height: 50
            }

            PropertyChanges {
                target: profiler_bloodystats_organizer
                width: 730
                height: 370
                opacity: 1
            }

            PropertyChanges {
                target: profiler_bloodystats_default_entry
                width: 730
                height: 40
                opacity: 1
            }

            PropertyChanges {
                target: profiler_bloodystats_default_name_text
                width: 600
                height: 40
                color: "#606060"
                text: qsTr("default")
                styleColor: "#000000"
                font.pixelSize: 18
                opacity: 1
            }

            PropertyChanges {
                target: profiler_bloodystats_profile1
                width: 730
                height: 40
                opacity: 1
            }

            PropertyChanges {
                target: profiler_bloodystats_profile1_text
                width: 600
                height: 40
                text: qsTr("choose your own name here")
                font.pixelSize: 18
                opacity: 1
            }

            PropertyChanges {
                target: row1
                width: 730
                height: 15
                opacity: 1
            }

            PropertyChanges {
                target: profiler_bloodystats_profile1_delete
                width: 25
                height: 40
                text: qsTr("-")
                font.bold: true
                horizontalAlignment: Text.AlignHCenter
                font.pixelSize: 24
                opacity: 1
            }

            PropertyChanges {
                target: profiler_bloodystats_profile1_save
                width: 28
                height: 28
                source: "img/save.svg"
                opacity: 1
            }

            PropertyChanges {
                target: profiler_bloodystats_add_profile
                width: 730
                height: 40
                opacity: 1
            }

            PropertyChanges {
                target: profiler_bloodystats_add_profile_add_text
                width: 40
                height: 40
                text: qsTr("+")
                horizontalAlignment: Text.AlignHCenter
                font.bold: true
                font.pixelSize: 24
                opacity: 1
            }
        }
    ]

    Row {
        id: bloodystats_settings_footer
        width: 200
        height: 400
        opacity: 0

        Item {
            id: bloodystats_settings_footer_placeholder1
            width: 200
            height: 200
            opacity: 0
        }



        Rectangle {
            id: bloodystats_settings_footer_simulate
            width: 200
            height: 200
            color: "#ffffff"
            opacity: 0

            Text {
                id: bloodystats_settings_footer_simulate_text
                text: qsTr("Text")
                anchors.fill: parent
                opacity: 0
                font.pixelSize: 12
            }
        }
        Item {
            id: bloodystats_settings_footer_placeholder2
            width: 200
            height: 200
            opacity: 0
        }

        Rectangle {
            id: bloodystats_settings_footer_save_simulate
            width: 200
            height: 200
            color: "#ffffff"
            opacity: 0

            Text {
                id: bloodystats_settings_footer_save_simulate_text
                text: qsTr("Text")
                anchors.fill: parent
                opacity: 0
                font.pixelSize: 12
            }
        }

        Rectangle {
            id: bloodystats_settings_footer_profiler_save
            width: 200
            height: 200
            color: "#ffffff"
            opacity: 0

            Text {
                id: bloodystats_settings_footer_profiler_save_text
                text: qsTr("Text")
                anchors.fill: parent
                font.pixelSize: 12
                opacity: 0
            }
        }
    }

    Rectangle {
        id: settings_mainarea_bloodystats_background
        width: 200
        height: 200
        color: "#ffffff"
        opacity: 0

        Column {
            id: settings_area
            x: 0
            y: 0
            width: 200
            height: 400
            opacity: 0



            Row {
                id: row
                width: 200
                height: 400
                opacity: 0


                Item {
                    id: item3
                    width: 200
                    height: 200
                    opacity: 0
                }
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


                Item {
                    id: item4
                    width: 200
                    height: 200
                    opacity: 0
                }
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

            ListView {
                id: listView
                x: 0
                y: 0
                width: 110
                height: 160
                delegate: Item {
                    width: 350
                    height: 35
                    Row {
                        id: row2
                        width: 350
                        height: 35

                        Text {
                            height: 35
                            text: name
                            verticalAlignment: Text.AlignTop
                            font.pointSize: 12
                            anchors.verticalCenter: parent.verticalCenter
                            font.bold: true
                        }

                        TextEdit {
                            id: textEdit
                            width: 200
                            height: 35
                            text: value_entry
                            font.pointSize: 12
                        }
                        spacing: 10
                    }
                }
                opacity: 0
                model: ListModel {
                    ListElement {
                        name: "wow class"
                        value_entry: "shaman"
                    }

                    ListElement {
                        name: "wow race"
                        value_entry: "draenei"
                    }

                    ListElement {
                        name: "wow spec"
                        value_entry: "elemental"
                    }

                    ListElement {
                        name: "talents"
                        value_entry: "3111231"
                    }
                }
            }
        }
    }

    Rectangle {
        id: profiler_bloodystats_background
        x: 20
        y: 60
        width: 200
        height: 200
        color: "#ffffff"
        opacity: 0

        Column {
            id: profiler_bloodystats_organizer
            width: 200
            height: 400
            opacity: 0



            Row {
                id: row1
                width: 200
                height: 400
                opacity: 0
            }
            Row {
                id: profiler_bloodystats_default_entry
                width: 200
                height: 400
                opacity: 0

                Text {
                    id: profiler_bloodystats_default_name_text
                    text: qsTr("Text")
                    font.pixelSize: 12
                    opacity: 0
                }
            }
            Row {
                id: profiler_bloodystats_profile1
                width: 200
                height: 400
                opacity: 0

                TextEdit {
                    id: profiler_bloodystats_profile1_text
                    width: 80
                    height: 20
                    text: qsTr("Text Edit")
                    font.pixelSize: 12
                    opacity: 0
                }


                Image {
                    id: profiler_bloodystats_profile1_save
                    width: 100
                    height: 100
                    source: "img/save.svg"
                    opacity: 0
                }
                Text {
                    id: profiler_bloodystats_profile1_delete
                    text: qsTr("Text")
                    font.pixelSize: 12
                    opacity: 0
                }
            }

            Row {
                id: profiler_bloodystats_add_profile
                width: 200
                height: 400
                opacity: 0

                Text {
                    id: profiler_bloodystats_add_profile_add_text
                    text: qsTr("Text")
                    font.pixelSize: 12
                    opacity: 0
                }
            }
        }
    }

    MouseArea {
        id: footer_simulate_mousearea
        width: 100
        height: 100
        opacity: 0
        onClicked: mainWindow.state = ""
    }

    MouseArea {
        id: footer_simulate_save_mousearea
        x: 6
        y: -3
        width: 100
        height: 100
        opacity: 0
        onClicked: mainWindow.state = ""
    }
}
