document.addEventListener('DOMContentLoaded', function() {
    const listingId = window.location.pathname.split('/').pop();
    fetch(`/api/listings/${listingId}`)
        .then(response => response.json())
        .then(data => {
            const listingDetailDiv = document.getElementById('listing-detail');
            listingDetailDiv.innerHTML = `<h2>${data.title}</h2><p>${data.description}</p><p>Price: ${data.price}</p>`;
        });
});