from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from tasks.models import TodoItem, Category
from django.core.cache import cache
import json
from collections import Counter
from collections import OrderedDict
import datetime

def index(request):

    # 1st version
    # counts = {t.name: random.randint(1, 100) for t in Tag.objects.all()}

    # 2nd version
    # counts = {t.name: t.taggit_taggeditem_items.count()
    # for t in Tag.objects.all()}

    # 3rd version
    from django.db.models import Count

    counts = Category.objects.annotate(total_tasks=Count(
        'todoitem')).order_by("-total_tasks")
    counts = {c.name: c.total_tasks for c in counts}

    priority = cache.get('priority', '')
    if priority == '':
        pr_counter = Counter()
        for td in TodoItem.objects.all():
            pr_counter[td.priority] += 1
        sorted(pr_counter.items())
        cache.set('priority', json.dumps(pr_counter))

    counts_pr = json.loads( cache.get('priority', '') )
    counts_pr = OrderedDict(sorted(counts_pr.items()))
    print(counts_pr)

    return render(request, "tasks/index.html", {"counts": counts, "counts_pr": counts_pr})

def date_cache(request):

    date_cache = cache.get('date_cache', '')
    if date_cache == '':
        date_cache = datetime.datetime.now()
        cache.set('date_cache', datetime.datetime.now(), 300)

    return render(request, "other/date_cache.html", {"date_cache": date_cache})

def filter_tasks(tags_by_task):
    return set(sum(tags_by_task, []))


def tasks_by_cat(request, cat_slug=None):
    u = request.user
    tasks = TodoItem.objects.filter(owner=u).all()

    cat = None
    if cat_slug:
        cat = get_object_or_404(Category, slug=cat_slug)
        tasks = tasks.filter(category__in=[cat])

    categories = []
    for t in tasks:
        for cat in t.category.all():
            if cat not in categories:
                categories.append(cat)

    return render(
        request,
        "tasks/list_by_cat.html",
        {"category": cat, "tasks": tasks, "categories": categories},
    )


class TaskListView(ListView):
    model = TodoItem
    context_object_name = "tasks"
    template_name = "tasks/list.html"

    def get_queryset(self):
        u = self.request.user
        qs = super().get_queryset()
        return qs.filter(owner=u)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_tasks = self.get_queryset()
        tags = []
        for t in user_tasks:
            tags.append(list(t.category.all()))

        categories = []
        for cat in t.category.all():
            if cat not in categories:
                categories.append(cat)
        context["categories"] = categories

        return context


class TaskDetailsView(DetailView):
    model = TodoItem
    template_name = "tasks/details.html"


