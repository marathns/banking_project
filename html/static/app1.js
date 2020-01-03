$(document).ready(function(){

	$('.updateButton').on('click',function() {

		var btn_id = $(this).attr('btn_id');
		var curr_date = $('#get_date').val();
		var category = $('#category_'+btn_id).val();

		req = $.ajax({
			url : '/budget_update',
			type : 'POST',
			data : { btn_id : btn_id, curr_date : curr_date, category : category }
		});

	});
});
