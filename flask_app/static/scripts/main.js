$(document).ready(function() {
    $('#player_results').dataTable({"paging": false, "searching": false, "order": [2, "desc"], "autoWidth": true});
    $('#team_results').dataTable({"paging": false, "searching": false, "order": [2, "desc"], "autoWidth": true});
    $('#club_results').dataTable({"paging": false, "searching": false, "order": [2, "desc"], "autoWidth": true});
    $('#game_history').dataTable({"paging": true, "searching": false, "order": [0, "desc"], "autoWidth": true, "pageLength": 25});
    $( ".datepicker" ).datepicker({dateFormat: "yy-mm-dd"});
} );