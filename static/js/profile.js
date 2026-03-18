document.addEventListener('DOMContentLoaded', function() {
    const walletAddress = '0xUserWallet'; // This would be dynamically set
    fetch(`/api/users/${walletAddress}`)
        .then(response => response.json())
        .then(data => {
            const profileDiv = document.getElementById('profile');
            profileDiv.innerHTML = `<h2>Wallet Address: ${data.wallet_address}</h2><p>${data.profile_info}</p>`;
        });
});