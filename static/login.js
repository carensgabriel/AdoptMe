$(document).ready(function () {
    $("form").submit(function (e) {
        e.preventDefault();
        let formData = {
            username: $("#username").val(),
            password: $("#password").val()
        };

        $.ajax({
            type: "POST",
            url: "/login",
            contentType: "application/json",
            data: JSON.stringify(formData),
            success: function (response) {
                if (response.success) {
                    window.location.href = response.redirect;
                } else {
                    alert(response.message);
                }
            }
        });
    });
});
