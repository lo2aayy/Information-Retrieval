$(document).ready(function() {
	$('#query').on('change', function(){
	  var val = $(this).val();
	  console.log(val);
	});
  	$("#query").keyup(function() {
	  	var lastQuery = localStorage.getItem("lastQuery");
	    var query = $("#query").val();
	    var host = window.location.host;
	    var url = "http://" + host;
	    if (lastQuery != query) {
	    	localStorage.setItem("lastQuery", query);
		    $.ajax({
			  type: "GET",
			  url: url,
			  data: ({q: query}),
			  dataType: 'text',
			  success: function(data){
			  	if (data.length > 0) {
				  	$('#autocomplete option').remove();
			  		var cities = jQuery.parseJSON(data);
				  	for(var i in cities){
				  		var x = document.createElement("OPTION");
				  		x.value = cities[i].city;
				  		$('#autocomplete').append(x);
				  	}
			  	}
			  },
		      error: function (jqXHR, textStatus, errorThrown) {
		      		console.log(textStatus);
		        }
			}); 
	    }
  	})
})


