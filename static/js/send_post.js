window.onload = function() {
    window.scrollTo(0, document.body.scrollHeight);
}

document.querySelector('.post-textarea').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        document.querySelector('.input_btn').click();
    }
});
