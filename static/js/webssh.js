function get_connect_info() {
    var host = $.trim($('#host').val());
    var port = $.trim($('#port').val());
    var user = $.trim($('#user').val());
    var auth = $("input[name='auth']:checked").val();
    var pwd = $.trim($('#password').val());
    var password = window.btoa(pwd);
    var ssh_key = null;

    if (auth === 'key') {
        var pkey = $('#pkey')[0].files[0];
        var csrf = $("[name='csrfmiddlewaretoken']").val();
        var formData = new FormData();

        formData.append('pkey', pkey);
        formData.append('csrfmiddlewaretoken', csrf);

        $.ajax({
            url: '/upload_ssh_key/',
            type: 'post',
            data: formData,
            async: false,
            processData: false,
            contentType: false,
            mimeType: 'multipart/form-data',
            success: function (data) {
                ssh_key = data;
            }
        });
    }

    var connect_info1 = 'host=' + host + '&port=' + port + '&user=' + user + '&auth=' + auth;
    var connect_info2 = '&password=' + password + '&ssh_key=' + ssh_key;
    var connect_info = connect_info1 + connect_info2;
    return connect_info;
}


function get_term_size() {
    var init_width = 9;
    var init_height = 17;

    var windows_width = $(window).width();
    var windows_height = $(window).height();

    return {
        cols: Math.floor(windows_width / init_width),
        rows: Math.floor(windows_height / init_height),
    }
}


function websocket() {
    var cols = get_term_size().cols;
    var rows = get_term_size().rows;
    var connect_info = get_connect_info();

    var term = new Terminal(
        {
            cols: cols,
            rows: rows,
            useStyle: true,
            cursorBlink: true,
        }),
        protocol = (location.protocol === 'https:') ? 'wss://' : 'ws://',
        socketURL = protocol + location.hostname + ((location.port) ? (':' + location.port) : '') +
            '/webssh/?' + connect_info + '&width=' + cols + '&height=' + rows;

    var sock;
    sock = new WebSocket(socketURL);


    // ?????? websocket ??????, ?????? web ??????
    sock.addEventListener('open', function () {
        $('#form').addClass('hide');
        $('#django-webssh-terminal').removeClass('hide');
        term.open(document.getElementById('terminal'));
    });

    // ?????????????????????????????????????????? web ??????
    sock.addEventListener('message', function (recv) {
        var data = JSON.parse(recv.data);
        var message = data.message;
        var status = data.status;
        if (status === 0) {
            term.write(message)
        } else {
            window.location.reload()
        }
    });

    /*
    * status ??? 0 ???, ?????????????????????????????? websocket ???????????????, data ??????????????????, ?????? cols ??? rows ??????
    * status ??? 1 ???, resize pty ssh ????????????, cols ??????????????????????????????, rows ??????????????????????????????, ?????? data ??????
    */
    var message = {'status': 0, 'data': null, 'cols': null, 'rows': null};

    // ???????????????????????????
    term.on('data', function (data) {
        message['status'] = 0;
        message['data'] = data;
        var send_data = JSON.stringify(message);
        sock.send(send_data)
    });

    // ?????????????????????, ?????????????????????????????????????????????
    $(window).resize(function () {
        var cols = get_term_size().cols;
        var rows = get_term_size().rows;
        message['status'] = 1;
        message['cols'] = cols;
        message['rows'] = rows;
        var send_data = JSON.stringify(message);
        sock.send(send_data);
        term.resize(cols, rows)
    });
    return false
}
