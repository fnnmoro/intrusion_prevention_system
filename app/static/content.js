function hiddenForm(msg) {
    var p = document.createElement('p')
    var text = document.createTextNode(msg);

    p.appendChild(text);
    document.querySelector('main').appendChild(p);
    document.getElementById('loading').style.display = 'none';
};

function hiddenTableData(tableIndex, tdIndex) {
    var table = document.getElementById('t'+tableIndex);
    var tdHidden = table.getElementsByClassName('hidden')[tdIndex];
    var tdNotHidden = table.getElementsByClassName('not-hidden')[tdIndex];

    if (tdHidden.style.display == '') {
        tdHidden.style.display = 'table-cell';
        tdNotHidden.style.display = 'none';
    } else if (tdHidden.style.display == 'none') {
        tdHidden.style.display = 'table-cell';
        tdNotHidden.style.display = 'none';
    } else {
        tdHidden.style.display = 'none';
        tdNotHidden.style.display = 'table-cell';
    };
};
