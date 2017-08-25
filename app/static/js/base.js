$(function () {
    $('#add_project').on('click', function () {
        var name = $('#new_project').val();
        $('#info').hide()
        if (name.trim().length == 0){
            document.getElementById('info').innerHTML = 'Cannot be blank!';
            $('#info').show()
        }
        console.log(name.trim().length);
        return;

        document.getElementById('result').innerHTML = '';
        if ( isNaN(try_to_guess)){
            document.getElementById('more_less').innerHTML = '';
            document.getElementById('result').innerHTML = 'Only numbers!';
            return;
        }
        var balance = $('#balance').val();
        $('#balance').attr({value: balance - 1});
        document.getElementById('attempt').innerHTML = balance;

        if (number_to_guess == try_to_guess){
            document.getElementById('more_less').innerHTML = 'Excellent!<br>You won!';
            $.post("/write_progress", {
                _token: token,
                user_id: user_id,
                progress: try_to_guess,
                status: "won"
            }).done(function (result) {
                if (result['result'] === true){
                    $('#send_number').hide();
                    $('#exit').hide();
                    $('#game_over').show();
                    return;
                } else {
                    alert('Something was wrong! (eq)');
                    return;
                }
            }).fail(function (result) {
                alert('Server error! (eq)');
            });
        }

        if(number_to_guess > try_to_guess){
            document.getElementById('more_less').innerHTML = 'More';
            $.post("/write_progress", {
                _token: token,
                progress: try_to_guess,
                user_id: user_id,
                status: 'inprocess'
            })
        } else if (number_to_guess < try_to_guess){
            document.getElementById('more_less').innerHTML = 'Less';
            $.post("/write_progress", {
                _token: token,
                progress: try_to_guess,
                user_id: user_id,
                status: 'inprocess'
            })
        }

        if (balance < 1 && number_to_guess != try_to_guess){
            document.getElementById('result').innerHTML = 'Sorry, you failed.';
            $('#exit').hide();
            $.post("/write_progress", {
                _token: token,
                user_id: user_id,
                progress: try_to_guess,
                status: "fail"
            }).done(function (result) {
                if (result['result'] === true){
                    $('#send_number').hide();
                    $('#game_over').show();
                } else {
                    alert('Something was wrong! (b)');
                }
            }).fail(function () {
                alert('Server error! (b)');
            });
        }

    });
});

$(function () {
    $('#get_stat').on('click', function () {
         var token = $('#csrf_token').val();
         var user_id = $('#user_id').val();

         $.post("/get_stat", {
            _token: token,
            user_id: user_id
         }).done(function (result) {
            var users_info = getInfo(result);
            var user_table = '<table border="1"><caption style="color:orange"><h4>Statistics table of the current user.</h4></caption>\
<tr>\
  <th>Number for guessing</th>\
  <th>Progress</th>\
  <th>Status</th>\
</tr>' + users_info + '</table>';
            document.getElementById('stat').innerHTML = user_table;
         }).fail(function () {
            alert('Server error!');
         });
   });
});


function getInfo(info) {
    var users_info = '';
    var i;
    var count = 0;
    var length_of_info = Object.keys(info).length;

    for (i = 0; i < length_of_info; i++) {
        var split_info = info[count].split(",");
        count++;
        users_info += '<tr><td>' + split_info[0] + '</td><td>' + split_info[1] + '</td><td>' + split_info[2] + '</td></tr>'
    }
    return users_info;
};


function endGame () {
    var token = $('#csrf_token').val();
    var user_id = $('#user_id').val();

    $.post("/end_game", {
        _token: token,
        user_id: user_id
    }).done(function (result) {
        console.log(result)
    });
}
