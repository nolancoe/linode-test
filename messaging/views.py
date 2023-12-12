from django.shortcuts import render, redirect, get_object_or_404
from .models import Message, Profile  # Import your models
from .forms import MessageForm
from django.http import JsonResponse
from django.db.models import Max, Q

def messages(request):
    sent_users = Profile.objects.filter(sent_messages__receiver=request.user).distinct()
    received_users = Profile.objects.filter(received_messages__sender=request.user).distinct()

    users_with_messages = sent_users | received_users

    # Create a list of tuples containing the user and their most recent timestamp
    users_with_timestamps = []

    for user in users_with_messages:
        user_has_unread_message = False  # Default value for each user

        # Fetch the most recent message timestamp for each user
        most_recent_message = Message.objects.filter(
            Q(sender=request.user, receiver=user) | Q(sender=user, receiver=request.user)
        ).order_by('-timestamp').first()

        if most_recent_message and most_recent_message.receiver == request.user and not most_recent_message.is_read:
            user_has_unread_message = True

        if most_recent_message:
            users_with_timestamps.append((user, most_recent_message.timestamp, user_has_unread_message))

    # Sort the users based on their most recent message timestamp
    users_with_timestamps.sort(key=lambda x: x[1], reverse=True)

    return render(request, 'messages.html', {
        'users_with_timestamps': users_with_timestamps,
    })

def message_details(request, username):
    other_user = get_object_or_404(Profile, username=username)
    
    sent_messages = Message.objects.filter(sender=request.user, receiver=other_user).order_by('timestamp')
    received_messages = Message.objects.filter(sender=other_user, receiver=request.user).order_by('timestamp')

    # Mark received messages as read when the page is loaded
    for message in received_messages:
        if not message.is_read:
            message.is_read = True
            message.save()

    all_messages = sent_messages | received_messages

    context = {
        'other_user': other_user,
        'all_messages': all_messages
    }
    
    return render(request, 'message_details.html', context)


def send_message(request, username):
    other_user = get_object_or_404(Profile, username=username)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['message_content']
            
            # Save the message
            Message.objects.create(sender=request.user, receiver=other_user, content=content)
            
            # Redirect to the message details page for the same user
            return redirect('message_details', username=username)
    else:
        form = MessageForm()
    
    context = {
        'other_user': other_user,
        'form': form,
    }
    
    return render(request, 'message_details.html', context)

