document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll('.rating-stars').forEach(ratingContainer => {
        const bookId = ratingContainer.getAttribute('data-book-id');
        const bookTitle = ratingContainer.getAttribute('data-book-title');
        const authorName = ratingContainer.getAttribute('data-author-name');
        const publicationYear = ratingContainer.getAttribute('data-publication-year');
        const imageUrl = ratingContainer.getAttribute('data-image-url');

        // Handle star click events
        ratingContainer.querySelectorAll('.star').forEach((star, index) => {
            star.addEventListener('click', () => {
                const rating = parseInt(star.getAttribute('data-rating'), 10); // Parse as integer

                // Highlight selected stars
                highlightStars(ratingContainer, index);

                // Send AJAX request
                fetch('/rate-book', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        book_id: bookId,
                        rating: rating,
                        book_title: bookTitle,
                        author_name: authorName,
                        publication_year: publicationYear,
                        image_url: imageUrl
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Rating saved successfully!');
                    } else {
                        console.error('Server Error:', data.error);
                        alert('Error: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Network Error:', error);
                    alert('An error occurred while submitting your rating.');
                });
            });

            // Handle hover effects
            star.addEventListener('mouseover', () => highlightStars(ratingContainer, index));
            star.addEventListener('mouseleave', () => resetStars(ratingContainer));
        });
    });
});

function highlightStars(container, upToIndex) {
    container.querySelectorAll('.star').forEach((star, index) => {
        if (index <= upToIndex) {
            star.style.color = 'gold';
        } else {
            star.style.color = '#ddd';
        }
    });
}

function resetStars(container) {
    container.querySelectorAll('.star').forEach(star => {
        if (!star.classList.contains('selected')) {
            star.style.color = '#ddd';
        }
    });
}
