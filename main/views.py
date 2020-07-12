from django.shortcuts import get_object_or_404, redirect, render
from .forms import EventForm
from .models import Event
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .serializers import EventSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
import logging
from django.http import JsonResponse
from django.forms.models import model_to_dict
from .tasks import event_send_mail


logger = logging.getLogger(__name__)



def dashboard(request):
    return render(request, 'main/dashboard.html')

def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            event_date = form.cleaned_data['event_date']
            email = form.cleaned_data['email']
            Event.objects.create(title=title, content=content,
                                            event_date=event_date, email=email)
            

            new_event = form.save()
            return JsonResponse({'event': model_to_dict(new_event)}, status=200)
    else:
        form = EventForm()

    context = {'form': form}
    return render(request, 'main/create_event.html', context)

def event_list(request):
    events = Event.objects.all()
    context = {'events': events}
    return render(request, 'main/event_list.html', context)


class EventView(APIView):
    def get(self, request):
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    def post(self, request):
        event = request.data.get('event')
        serializer = EventSerializer(data=event)
        if serializer.is_valid(raise_exception=True):
            event_saved = serializer.save()
        else:
            logger.error("Сериализатор неккоректен в методе post")
        return Response(serializer.data)
    
    def put(self, request, pk):
        saved_event = get_object_or_404(Event.objects.all(), pk=pk)
        data = request.data.get('event')
        serializer = EventSerializer(
            instance=saved_event, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            event_saved = serializer.save()
        else:
            logger.error("Сериализатор неккоректен в методе put")
        return Response({
            "success": "Event '{}' updated successfully".format(event_saved.title)
        })
    
    def delete(self, request, pk):
        event = get_object_or_404(Event.objects.all(), pk=pk)
        event.delete()
        return Response({
            "message": "Event with title `{}` has been deleted.".format(event.title)
        }, status=204)

  



