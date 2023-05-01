CKEDITOR.editorConfig = function(config) {
    config.toolbarGroups = [
        { name: 'clipboard', groups: ['clipboard', 'undo'] },
        { name: 'editing', groups: ['find', 'selection', 'spellchecker', 'editing'] },
        { name: 'basicstyles', groups: ['basicstyles', 'cleanup'] },
        { name: 'paragraph', groups: ['list', 'indent', 'blocks', 'align', 'bidi', 'paragraph'] },
        { name: 'links', groups: ['links'] },
        { name: 'insert', groups: ['insert'] },
        { name: 'styles', groups: ['styles'] },
        { name: 'colors', groups: ['colors'] },
        { name: 'tools', groups: ['tools'] },
        { name: 'others', groups: ['others'] },
        { name: 'about', groups: ['about'] }
    ];

    config.removeButtons = 'Save,Templates,ExportPdf,Preview,Print,Table,Flash,Image,HorizontalRule,Smiley,SpecialChar,PageBreak,Iframe,Unlink,Link,Anchor,Language,BidiRtl,BidiLtr, Blockquote,Form,Checkbox,Radio,TextField,Textarea,Button,Select,HiddenField,About,NewPage,Source,CreateDiv,Styles,Format,Subscript,Superscript';
};