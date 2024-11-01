import QtQuick
import QtQuick.Controls

Row {
    id: root
    property int frameCounter: 0
    property int frameCounterAvg: 0
    property int counter: 0
    property int fps: 0
    property int fpsAvg: 0
    Label {
        color: "#c0c0c0"
        text: root.fpsAvg + " | " + root.fps + " fps"
    }
    Image {
        anchors.verticalCenter: parent.verticalCenter
        width: 14
        height: 14
        source: "qrc:/qt/qml/Gallery/res/image/ic_spinner.png"
        NumberAnimation on rotation {
            from:0
            to: 360
            duration: 800
            loops: Animation.Infinite
        }
        onRotationChanged: frameCounter++
    }
    Timer {
        interval: 2000
        repeat: true
        running: true
        onTriggered: {
            frameCounterAvg += frameCounter
            root.fps = Math.ceil(frameCounter / 2);
            counter++;
            frameCounter = 0
            if (counter >= 3) {
                root.fpsAvg = Math.ceil(frameCounterAvg / (2 * counter))
                frameCounterAvg = 0
                counter = 0
            }
        }
    }
}
