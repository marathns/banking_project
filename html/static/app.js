$(document).ready(function(){

	$('.updateButton').on('click',function() {

		var tran_id = $(this).attr('tran_id');
		var actual_amount = $('#actual_amount'+tran_id).val();
		var category = $('#category'+tran_id).val();

		req = $.ajax({
			url : '/update',
			type : 'POST',
			data : { actual_amount : actual_amount, category : category, tran_id : tran_id}
		});

	});
});
