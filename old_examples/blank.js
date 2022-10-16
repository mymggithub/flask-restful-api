
	function track_look_at_followers() {
		// var requestDetails = {
		// 	method: "GET",
		// 	url: "http://192.168.1.40:5000/",
		// 	headers: { "Content-Type": "application/json" },
		// 	onload: function(response) {
		// 		console.log(response.responseText);
		// 	}
		// };
		// GM_xmlhttpRequest(requestDetails);
	};


	// Track pages that don't really reload, but refresh the entire content (like youtube).
	var mutationObserver = new MutationObserver(function(mutations) {
		mutations.forEach(function(mutation) {
			if (oldHref != document.location.href) {
				oldHref = document.location.href;
				track();
				return true;
			}
		});
	});