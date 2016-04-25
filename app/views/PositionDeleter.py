from app.models import Position, Employee
def deleteposition(self, request, *args, **kwargs):
    pos = self.get_object()
    Employee.objects.filter(position=pos).update(position=None)
    return super(PositionDelete, self).delete(request, *args, **kwargs)