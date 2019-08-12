function hiddenForm(msg) {
    var p = document.createElement('p')
    var text = document.createTextNode(msg);

    p.appendChild(text);
    document.querySelector('main').appendChild(p);
    document.getElementById('loading').style.display = 'none';
};
