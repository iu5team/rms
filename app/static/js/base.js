
$(function () {
    $(".datepicker").datepicker();

    $(".datepicker-employee-calendar").datepicker({
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
                alert("Error:" + data);
            });
        },
        beforeShowDay: function(date){
            var allowedTasksDates = window.allowedTasksDates;
            var vacationDates = window.vacationDates;
            var medicalDates = window.medicalDates;
            var string;
            if (vacationDates != null) {
                string = $.datepicker.formatDate('yy-mm-dd', date);
                if (vacationDates.indexOf(string) != -1) {
                    return [true, 'calendar-vacation'];
                }
            }
            if (medicalDates != null) {
                string = $.datepicker.formatDate('yy-mm-dd', date);
                if (medicalDates.indexOf(string) != -1) {
                    return [true, 'calendar-medical'];
                }
            }
            if (allowedTasksDates != null) {
                string = $.datepicker.formatDate('yy-mm-dd', date);
                return [allowedTasksDates.indexOf(string) != -1];
            }
            return [1]
        }
    });
});
