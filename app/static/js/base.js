
class AbstractMediator {
    notifyChanged(object, data) {
        throw new TypeError("not implemented");
    }
}

class Mediator extends AbstractMediator {
    constructor() {
        super();
        this.taskList = null;
        this.calendar = null;
    }

    setTaskList(taskList) {
        this.taskList = taskList;
        this.taskList.setMediator(this);
    }

    setCalendar(calendar) {
        this.calendar = calendar;
        this.calendar.setMediator(this);
    }

    notifyChanged(object, data) {
        if (object == this.calendar) {
            return this.taskList.notify(data);
        }
        if (object == this.taskList) {
            return this.calendar.notify(data);
        }
    }
}

class Widget {
    constructor() {
        this.mediator = null;
    }

    setMediator(mediator) {
        this.mediator = mediator;
    }

    notify(data) {
        throw new TypeError("not implemented");
    }
}

class TaskList extends Widget {
    constructor($obj) {
        super();
        this.$obj = $obj;
    }

    notify(data) {
        $.ajax('/api/tasks_by_date', {
            method: 'GET',
            data: {
                assignee: data.assignee,
                date: data.date
            }
        }).done(data => this.$obj.html(data))
          .error(data => alert("Error:" + data))
        ;
    }
}

class Calendar extends Widget {
    constructor($obj) {
        super();
        this.$obj = $obj;

        let self = this;
        this.$obj.datepicker({
            inline: true,
            dateFormat: 'yy-mm-dd',
            onSelect: function(dateText, inst) {
                var assignee = $('.employee__id').val();
                var date = $(this).val();

                self.mediator.notifyChanged(self, {assignee, date});
            },
            beforeShowDay: function(date){
                var allowedTasksDates = window.allowedTasksDates;
                var vacationDates = window.vacationDates;
                var medicalDates = window.medicalDates;
                var string;
                if (vacationDates != null) {
                    string = $.datepicker.formatDate('yy-mm-dd', date);
                    if (vacationDates[string]) {
                        return [true, 'calendar-vacation'];
                    }
                }
                if (medicalDates != null) {
                    string = $.datepicker.formatDate('yy-mm-dd', date);
                    if (medicalDates[string]) {
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

        var clicks = 0;
        var isDblClick = false;
        this.$obj.find('a').contextmenu(function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log(clicks, isDblClick);
            var allSpecialDates = window.allSpecialDates;

            var $this = $(this);
            var $datepicker = $this.parents('.datepicker-employee-calendar');
            var selectedDay = $this.text();

            var date = $datepicker.datepicker("getDate");
            date.setDate(selectedDay);

            var dateString = $.datepicker.formatDate('yy-mm-dd', date);
            var obj = allSpecialDates[dateString];
            if (obj) {
                console.log(obj);
            }
            window.location.href = '/calendar/update/' + obj;
        });
    }
}


$(function () {
    $(".datepicker").datepicker();

    let mediator = new Mediator();
    let calendar = new Calendar($(".datepicker-employee-calendar"));
    let taskList = new TaskList($('.calendar-tasks'));

    mediator.setCalendar(calendar);
    mediator.setTaskList(taskList);
});
