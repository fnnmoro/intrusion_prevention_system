function hiddenForm() {
    var p = document.createElement('p')
    var text = document.createTextNode('Loading...');

    p.appendChild(text);
    document.querySelector('main').appendChild(p);
    document.getElementById('loading').style.display = 'none';
};
