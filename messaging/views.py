from django.shortcuts import render, redirect, get_object_or_404
from .models import Message, Profile  # Import your models
from .forms import MessageForm

def messages(request):
    # Get users based on sent or received messages by the current user
    sent_users = Profile.objects.filter(sent_messages__receiver=request.user).distinct()
    received_users = Profile.objects.filter(received_messages__sender=request.user).distinct()
    
    users_with_messages = sent_users | received_users  # Merge the two querysets without duplicates
    
    return render(request, 'messages.html', {'users_with_messages': users_with_messages})


def message_details(request, username):
    other_user = get_object_or_404(Profile, username=username)
    
    sent_messages = Message.objects.filter(sender=request.user, receiver=other_user).order_by('timestamp')
    received_messages = Message.objects.filter(sender=other_user, receiver=request.user).order_by('timestamp')
    
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