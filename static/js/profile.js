function changeEmail() {
    var email = document.getElementById('email').value;
    fetch('/change_email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: 'email=' + email
    })
    .then(response => response.text())
    .then(data => {
        if (data.includes('Ошибка')) {
            alert(data);
        } else {
            window.location.reload();
        }
    })
    .catch(error => console.error('Ошибка:', error));
}

function changePassword() {
    var newPassword = document.getElementById('new-password').value;
    var confirmPassword = document.getElementById('confirm-password').value;
    if (newPassword !== confirmPassword) {
        alert('Пароли не совпадают');
        return;
    }
    fetch('/change_password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: 'new-password=' + newPassword + '&confirm-password=' + confirmPassword
    })
    .then(response => response.text())
    .then(data => {
        if (data.includes('Ошибка')) {
            alert(data);
        } else {
            window.location.reload();
        }
    })
    .catch(error => console.error('Ошибка:', error));
}