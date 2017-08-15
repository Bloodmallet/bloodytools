import QtQuick 2.6
import QtQuick.Controls 2.1

Rectangle {
    id: mainWindow

    width: 750
    height: 500
    property alias top_menu_profiler_profile_picker: top_menu_profiler_profile_picker
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
                target: row
                width: 710
                height: 40
                opacity: 1
            }

            PropertyChanges {
                target: text1
                width: 710
                height: 40
                text: qsTr("General")
                font.pixelSize: 24
                font.bold: true
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                opacity: 1
            }

            PropertyChanges {
                target: options_grid
                width: 710
                height: 300
                cellHeight: 25
                cellWidth: 350
                clip: true
                contentWidth: 350
                contentHeight: 50
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

                Text {
                    id: text1
                    text: qsTr("Text")
                    font.pixelSize: 12
                    opacity: 0
                }
            }

            GridView {
                id: options_grid
                x: 0
                y: 0
                width: 140
                height: 140
                cellHeight: 70
                opacity: 0
                cellWidth: 70
                model: ListModel {
                    ListElement {
                        option_name: "Class"
                        option_value: "Shaman"
                    }
                    ListElement {
                        option_name: "Spec"
                        option_value: "Elemental"
                    }
                    ListElement {
                        option_name: "Race"
                        option_value: "Draenei"
                    }
                    ListElement {
                        option_name: "Talents"
                        option_value: "3111231"
                    }
                    ListElement {
                        option_name: "Fight style"
                        option_value: "Patchwerk"
                    }

                    ListElement {
                        option_name: "Profile"
                        option_value: "T20M"
                    }
                    ListElement {
                        option_name: "Tier set number"
                        option_value: "20"
                    }
                    ListElement {
                        option_name: "Force 2p bonus"
                        option_value: "False"
                    }
                    ListElement {
                        option_name: "Force 4p bonus"
                        option_value: "False"
                    }

                    ListElement {
                        option_name: "Crit lower bound"
                        option_value: "3500"
                    }
                    ListElement {
                        option_name: "Haste lower bound"
                        option_value: "3500"
                    }
                    ListElement {
                        option_name: "Mastery lower bound"
                        option_value: "3500"
                    }
                    ListElement {
                        option_name: "Versatility lower bound"
                        option_value: "2000"
                    }
                    ListElement {
                        option_name: "General upper bound"
                        option_value: "13500"
                    }

                    ListElement {
                        option_name: "Calculation method"
                        option_value: "differential_evolution"
                    }
                    ListElement {
                        option_name: "Output"
                        option_value: "txt"
                    }
                    ListElement {
                        option_name: "Custom character stats"
                        option_value: "False"
                    }
                    ListElement {
                        option_name: "Custom fight style"
                        option_value: "False"
                    }
                    ListElement {
                        option_name: "Generate html"
                        option_value: "False"
                    }
                    ListElement {
                        option_name: "SimC path"
                        option_value: "../simc.exe"
                    }
                    ListElement {
                        option_name: "Default actions"
                        option_value: "True"
                    }
                    ListElement {
                        option_name: "Iterations"
                        option_value: "250000"
                    }
                    ListElement {
                        option_name: "Target error"
                        option_value: "0.1"
                    }
                    ListElement {
                        option_name: "Threads"
                        option_value: ""
                    }
                    ListElement {
                        option_name: "PTR"
                        option_value: "False"
                    }
                }
                delegate: Item {
                    width: 350
                    height: 25

                    Row {
                        id: options_grid_row
                        width: 350
                        height: 25

                        Text {
                            id: options_grid_row_name
                            y: 3
                            width: 175
                            height: 25
                            text: option_name
                            verticalAlignment: Text.AlignTop
                            font.pixelSize: 16
                        }

                        Rectangle {
                            id: rectangle
                            y: 2
                            width: 172
                            height: 22
                            color: "#ffffff"
                            radius: 1
                            border.color: "#aaaaaa"
                            border.width: 1

                            TextEdit {
                                id: options_grid_row_value
                                x: 2
                                width: 170
                                height: 25
                                text: option_value
                                font.pixelSize: 16
                            }
                        }
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
