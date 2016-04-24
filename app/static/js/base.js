
$(function () {
    $(".datepicker").datepicker();

    $(".datepicker-inline").datepicker({
        inline: true,
        dateFormat: 'yy-mm-dd',
        onSelect: function(dateText, inst) {
            var date = $(this).val();
            var assignee = $('.employee__id').val();
            var $tasksList = $('.calendar-tasks');
            $.ajax('/api/tasks_by_date', {
                method: 'GET',
                data: {
                    assignee: assignee,
                    date: date
                }
            }).done(function(data) {
                $tasksList.html(data)
            }).error(function(data) {
                alert("Error: data");
            });
        },
        beforeShowDay: function(date){
            var allowedTasksDates = window.allowedTasksDates;
            if (typeof(allowedTasksDates ) !== 'undefined' && allowedTasksDates != null && allowedTasksDates.length > 0) {
                var string = $.datepicker.formatDate('yy-mm-dd', date);
                return [allowedTasksDates.indexOf(string) != -1];
            }
            return [1]
        }
    });
});
