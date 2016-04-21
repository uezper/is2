$(document).ready(function(){
	
	adjustTest();
	
	$(window).resize(function(){
		adjustTest();
		if ($(".topBar").width() == $(".sideBar").width()) $("#sideBar-extension").hide();
		else $("#sideBar-extension").show();
	});
	function adjustTest()
	{
		$("#sideBar-extension").css({ 
		"width": $(".sideBar").width(),
		"top": $(".topBar").height() + $(".sideBar").height(),
		});
	}
});