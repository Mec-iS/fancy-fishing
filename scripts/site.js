/*
$(function () {
    
    SyntaxHighlighter.all();

 } ());
*/
function showNewSlug() {

    var type = $('#action_type').val();

    if (type !== 'new') {
        $('#new_slug').hide();
        $('#edit_slug').show();
    }
    else {
        $('#new_slug').show();
        $('#edit_slug').hide();
    }
}