$('.login_btn').on('click', function(){
    let email = $('#id_email').val();
    let password = $('#id_password').val();
    let url = login_view
    $.ajax({
        url: url,
        type: 'POST',
        dataType : 'json',
        headers: { "X-CSRFToken": csrf },
        data:{
          'csrfmiddlewaretoken': csrf,
          'email': email,
          'password': password,
        },
        success(json){
            if(json.status == 1){
                window.location = dashboard_view
            }else{
                console.log(json)
                if(json.errors){
                    console.log(json.errors);
                    $('.login-policy').show().fadeOut(5000);
                }
            }
        }
    })
})