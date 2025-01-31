document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    const searchResultsContainer = document.querySelector('.search-results-container');

    let debounceTimer;

    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            const query = this.value;

            if (query.length >= 2   ) {
                fetch('/search_threads?query=' + encodeURIComponent(query))
                    .then(response => response.json())
                    .then(data => {
                        searchResults.innerHTML = '';
                        if (data.length === 0) {
                            searchResults.innerHTML = '<div class="search-item">Ничего не найдено</div>';
                        } else {
                            data.forEach(thread => {
                                const div = document.createElement('div');
                                div.className = 'search-item';
                                div.textContent = thread.title;
                                div.addEventListener('click', () => {
                                    window.location.href = '/thread/' + thread.id;
                                });
                                searchResults.appendChild(div);
                            });
                        }
                        searchResultsContainer.style.display = 'block';
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        searchResults.innerHTML = '<div class="search-item">Произошла ошибка при поиске</div>';
                        searchResultsContainer.style.display = 'block';
                    });
            } else {
                searchResults.innerHTML = '';
                searchResultsContainer.style.display = 'none';
            }
        }, 300);
    });

    // Скрываем результаты при клике вне поля поиска
    document.addEventListener('click', function(event) {
        if (!searchInput.contains(event.target) && !searchResultsContainer.contains(event.target)) {
            searchResultsContainer.style.display = 'none';
        }
    });
});
