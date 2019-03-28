$(function() {
    $('#clear-dropzone').on('click', function(e) {
        Dropzone.forElement("#split-dropzone").removeAllFiles(true);
    });
});