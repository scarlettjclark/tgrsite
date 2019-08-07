from django.contrib.auth.decorators import login_required
from django.contrib.messages import add_message, constants
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, AccessMixin

from notifications.models import notify, NotifType
from .forms import ThreadForm, ResponseForm, ThreadEditForm
from .models import Thread, Response, Forum


# landing page: "root forum"
def index(request):
    context = {
        'forums': Forum.get_parentless_forums().order_by('sort_index'),
        'current': 'Forum',
    }
    return render(request, 'forum/forum.html', context)


class RootForum(ListView):
    model = Forum
    template_name = "forum/forum.html"
    context_object_name = "forums"

    def get_queryset(self):
        return Forum.get_parentless_forums().order_by('sort_index')


class ViewSubforum(AccessMixin, SuccessMessageMixin, CreateView):
    model = Thread
    form_class = ThreadForm
    template_name = "forum/subforum.html"
    success_message = "Thread successfully created"

    def post(self, request, *args, **kwargs):
        # Login required but only for post
        if not request.user.is_authenticated:
            self.handle_no_permission()
        else:
            return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_forum = get_object_or_404(Forum, id=self.kwargs['forum'])
        # put pinned/stickied threads first
        threads = Thread.objects.filter(forum_id=self.kwargs['forum']).extra(order_by=['-is_pinned', '-pub_date'])
        context.update({
            'current': current_forum,
            'forums': current_forum.get_subforums().order_by('sort_index'),
            'threads': threads
        })
        return context

    def form_valid(self, form):
        """
        title=form.cleaned_data['title'],
        body=form.cleaned_data['body'],
        author=request.user.member,
        pub_date=timezone.now(),
        forum=Forum.objects.get(id=request.POST.get('forum')),
        """
        form.instance.author = self.request.user.member
        form.instance.pub_date = timezone.now()
        form.instance.forum = Forum.objects.get(id=self.kwargs['forum'])
        return super().form_valid(form)


class ViewThread(AccessMixin, SuccessMessageMixin, CreateView):
    model = Response
    form_class = ResponseForm
    template_name = "forum/thread.html"
    success_message = "Response successfully created"

    def post(self, request, *args, **kwargs):
        # Login required but only for post
        if not request.user.is_authenticated:
            self.handle_no_permission()
        else:
            return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'thread': get_object_or_404(Thread, id=self.kwargs['thread']),
            'responses': Response.objects.filter(thread=self.kwargs['thread']).order_by('pub_date'),
        })
        return context

    def form_valid(self, form):
        """
        body=form.cleaned_data['body'],
        author=request.user.member,
        pub_date=timezone.now(),
        thread=thread,
        """
        thread = Thread.objects.get(id=self.kwargs['thread'])

        form.instance.author = self.request.user.member
        form.instance.pub_date = timezone.now()
        form.instance.thread = thread

        # Create Notifications
        url = reverse('forum:viewthread', kwargs={'thread': self.kwargs['thread']})
        for author in thread.get_all_authors():
            if author != self.request.user.member:
                notify(author, NotifType.FORUM_REPLY,
                       '{} replied to a thread you\'ve commented in!'.format(self.request.user.username), url,
                       thread.id)

        return super().form_valid(form)


class DeleteThread(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Thread
    success_message = "Thread Deleted"
    template_name = "forum/delete_thread.html"

    def test_func(self):
        thread = get_object_or_404(Thread, id=self.kwargs['pk'])
        return self.request.user.member == thread.author

    def get_success_url(self):
        return reverse('forum:subforum', kwargs={'forum': self.object.forum.id})


class DeleteResponse(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Response
    success_message = "Response Deleted"
    template_name = "forum/delete_response.html"

    def test_func(self):
        response = get_object_or_404(Response, id=self.kwargs['pk'])
        return self.request.user.member == response.author

    def get_success_url(self):
        return reverse('forum:viewthread', kwargs={'thread': self.object.thread.id})


class EditResponse(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Response
    form_class = ResponseForm
    template_name = "forum/edit_response.html"
    success_message = "Response changed"

    def test_func(self):
        response = get_object_or_404(Response, id=self.kwargs['pk'])
        return self.request.user.member == response.author

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


@login_required
def edit_thread_view(request, pk):
    thread = get_object_or_404(Thread, id=pk)
    if thread.author.equiv_user.id != request.user.id:
        # TODO: placeholder error
        return HttpResponseForbidden()
    form = ThreadEditForm(instance=thread)
    context = {'form': form, 'id': pk}
    return render(request, 'forum/edit_thread.html', context)


@login_required
def edit_response_view(request, pk):
    response = get_object_or_404(Response, id=pk)
    if response.author.equiv_user.id != request.user.id:
        return HttpResponseForbidden()
    form = ResponseForm(instance=response)
    context = {'form': form, 'id': pk}
    return render(request, 'forum/edit_response.html', context)


@login_required
def edit_thread_process(request):
    id = request.POST.get('id')
    if (request.method != 'POST'):
        return HttpResponseRedirect("/")

    thread = get_object_or_404(Thread, id=id)

    # first, standard permissions junk
    if thread.author.equiv_user.id != request.user.id:
        return HttpResponseForbidden()

    form = ThreadEditForm(request.POST, instance=thread)
    if (form.is_valid()):
        form.save()
        res = HttpResponseRedirect(reverse('forum:viewthread', kwargs={'pk': id}))
    else:
        add_message(request, constants.ERROR, "Unable to edit post.")
        res = HttpResponseRedirect(reverse('forum:viewthread', kwargs={'pk': id}))
    return res


@login_required
def edit_response_process(request):
    id = request.POST.get('id')
    if (request.method != 'POST'):
        return HttpResponseRedirect("/")

    response = get_object_or_404(Response, id=id)

    # first, standard permissions junk
    if response.author.equiv_user.id != request.user.id:
        return HttpResponseForbidden()

    form = ResponseForm(request.POST, instance=response)
    if (form.is_valid()):
        form.save()
        res = HttpResponseRedirect(reverse('forum:viewthread', kwargs={'pk': response.thread.id}))
    else:
        add_message(request, constants.ERROR, "Unable to edit response.")
        res = HttpResponseRedirect(reverse('forum:viewthread', kwargs={'pk': response.thread.id}))
    return res
