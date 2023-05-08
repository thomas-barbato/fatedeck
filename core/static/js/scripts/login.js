$('.login_btn').on('click', function(){
    let email = $('#id_email').val();
    let password = $('#id_password').val();
    let url = login_view;
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
                window.location = dashboard_view;
            }else{
                if(json.errors){
                    $('.login-policy').show().fadeOut(5000);
                }
            }
        }
    })
})