$(function() {

    $('#destination').autocomplete({
        source: '/suggest',
        minLength: 0
    })

    $('#destination_all').click(function(e) {
        $('#destination').autocomplete("search");
    });

    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })

});
