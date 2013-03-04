function tag(){
	var new_pages = $('#new_pages').val();
	if (new_pages.trim().length != 0){
		$.post('/addNewPage', {'new_pages' : new_pages}, function(js) {
			$('#result').html( js );
			});
	}else{
		$('#new_pages').css('box-shadow','1px 1px 1px #FF5555');
		$('#new_pages').css('border-top','1px solid #FF5555');
		$('#new_pages').css('border-left','1px solid #FF5555');
	}
}