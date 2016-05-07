$(document).ready(function(){
	
	adjustTest();
	

	$(window).resize(function(){
		adjustTest();	
	});

	function adjustTest()
	{

		$("#sideBar-extension").css({ 
		"width": $(".sideBar").width(),
		"top": $(".topBar").height() + $(".sideBar").height(),
		"min-height": $(".mainContent").height() - $(".sideBar").height(),
		});

		if ($(".topBar").width() == $(".sideBar").width()) $("#sideBar-extension").hide();
		else $("#sideBar-extension").show();
	}
});
