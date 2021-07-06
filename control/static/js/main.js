$(function() {

    $('#destination').autocomplete({
        source: '/suggest',
        minLength: 0,
        focus: function( event, ui ) {
            $( "#destination" ).val( ui.item.label );
            return false;
        },
        select: function( event, ui ) {
            $( "#destination" ).val( ui.item.label );
            $("#index").val(ui.item.value);
            return false;
        }
    })

    $('#destination_all').click(function() {
        $('#destination').autocomplete("search");
    });

    function set_date_stop() {
        let date = new Date($('#tour_date_start').val());
        let newdate = new Date(date);

        newdate.setDate(newdate.getDate() + 14);

        let dd = newdate.getDate();
        let mm = newdate.getMonth() + 1;
        let yy = newdate.getFullYear();

        let someFormattedDate = yy + '-' + ('0' + mm).slice(-2) + '-' + ('0' + dd).slice(-2);
        $('#tour_date_stop').val(someFormattedDate)
    }

    $('#tour_date_start').change(function() {
        set_date_stop()
    });


    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })

});
