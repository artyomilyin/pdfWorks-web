$('body').tooltip({
    selector: '[rel="tooltip"]',
    trigger: 'hover'
});


$(function() {
	$("#merge-dropzone").sortable({
        items:'.dz-preview',
        cursor: 'move',
        opacity: 0.5,
        containment: '#merge-dropzone',
        distance: 20,
        tolerance: 'pointer'
    });
});
$(function() {
    $('#merge-dropzone').submit(function(e) {
        if ($('#merge-dropzone-submit-btn').hasClass('disabled') === true) {
            e.preventDefault();
            return;
        }
        var files = $('#merge-dropzone>div.dz-success');
        var order_array = [];
        files.each(function(index, file){
          order_array.push($(file).attr("file_uuid"));
        });
        order_array_input = $('<input />').attr('type', 'hidden')
          .attr('name', 'order_array')
          .attr('value', order_array);
        order_array_input.appendTo('#merge-dropzone');
        e.preventDefault();
        this.submit();
        children = $('#merge-dropzone>div.dz-preview');
        order_array_input.remove();
        Dropzone.forElement("#merge-dropzone").removeAllFiles(true);
        $('#merge-dropzone-submit-btn').addClass('disabled')
            .attr("rel", "tooltip")
            .attr("data-title", "Upload some files first");
    });
});