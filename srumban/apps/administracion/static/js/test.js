document.getElementById("button1").addEventListener('click', function () {
    var text = document.getElementById('textbox1');
    text.text = "TEXTO2";
    print("Boton1");
    print(text.text);
    c = 1/0;
});

document.getElementById("link1").addEventListener('click', function(){
    var text = document.getElementById('textbox1');
       text.text = "TEXTO1";
});



