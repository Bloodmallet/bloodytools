import QtQuick 2.6
import QtQuick.Window 2.2

Window {
    visible: true
    width: 750
    height: 500
    title: qsTr("Bloodytools")
    minimumHeight: 500
    minimumWidth: 750


    MainForm {
        mouseArea1.onClicked: {
            console.log(qsTr("Clicked on Bloodystats mousearea."))
        }
        button.onClicked: {
            console.log(qsTr("Clicked on Bloodytrinkets button."))
        }
        anchors.fill: parent
        mouseArea.onClicked: {
            console.log(qsTr('Clicked on background.'))
        }
    }
}
