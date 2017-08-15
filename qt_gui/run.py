import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication
from PyQt5.QtQuick import QQuickView

# Main Function
if __name__ == '__main__':
    # Create main app
    myApp = QApplication(sys.argv)
    # Create a label and set its properties
    appLabel = QQuickView()
    appLabel.setSource(QUrl('main.qml'))

    # Show the Label
    appLabel.show()

    # Execute the Application and Exit
    myApp.exec_()
    sys.exit()