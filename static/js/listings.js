document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/listings')
        .then(response => response.json())
        .then(data => {
            const listingsDiv = document.getElementById('listings');
            data.forEach(listing => {
                const listingElement = document.createElement('div');
                listingElement.className = 'listing';
                listingElement.innerHTML = `<h2>${listing.title}</h2><p>${listing.description}</p><p>Price: ${listing.price}</p>`;
                listingsDiv.appendChild(listingElement);
            });
        });
});