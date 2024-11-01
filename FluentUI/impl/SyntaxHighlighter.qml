import QtQuick
import FluentUI.impl

Objects {
    id: control
    default property list<TextCharFormat> children
    property alias textDocument: syntax_highlighter_impl.textDocument
    signal highlightBlockChanged(var text)
    SyntaxHighlighterImpl {
        id: syntax_highlighter_impl
        onHighlightBlockChanged: (text)=>{control.highlightBlockChanged(text)}
    }
    function setFormat(start,count,format){
        syntax_highlighter_impl.setFormat(start,count,format)
    }
}
