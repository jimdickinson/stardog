function executeSearch() {
    var searchText = document.getElementById("searchInput").value;
    var xhr = new XMLHttpRequest();
    var host = location.hostname;
    var port = location.port;
    var protocol = location.protocol;
    var pathname = location.pathname;
    var baseUrl = protocol + '//' + host + (port !== '' ? ':' + port : '');
    var collectionName = undefined;
    if (pathname.includes('pods')) {
        collectionName = 'pods';
    } else if (pathname.includes('namespaces')) {
        collectionName = 'namespaces';
    } else if (pathname.includes('deployments')) {
        collectionName = 'deployments';
    } else {
        return;
    }
    var searchURL = baseUrl + '/api/rest/v2/namespaces/stardog/collections/' + collectionName + '?where=' + encodeURIComponent(searchText) + "&pretty=true&raw=true";
    xhr.open('GET', searchURL);

    xhr.onload = function() {
        document.getElementById("searchResult").innerText = (xhr.status > 399 ? 'Error: ' : '') + xhr.response;
        if (xhr.status == 204) {
            document.getElementById("searchResult").innerText = "No Results";
        }
    };
    
    xhr.onerror = function() {
        document.getElementById("searchResult").innerText = 'Unspecified Network Error';
    };

    xhr.send(null);
}