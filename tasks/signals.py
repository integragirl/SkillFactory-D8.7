import json

from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from tasks.models import TodoItem, Category
from collections import Counter

from django.core.cache import cache

@receiver(post_save, sender=TodoItem)
def task_priority(sender, instance, **kwargs):
    print('task_priority - post_save')
    pr_counter = Counter()
    for td in TodoItem.objects.all():
        pr_counter[td.priority] += 1
    sorted(pr_counter.items())
    print(pr_counter)
    cache.set('priority', json.dumps(pr_counter) )

@receiver(m2m_changed, sender=TodoItem.category.through)
def task_cats_added(sender, instance, action, model, **kwargs):
    if action != "post_add":
        return

    for cat in instance.category.all():
        slug = cat.slug

        new_count = 0
        for task in TodoItem.objects.all():
            new_count += task.category.filter(slug=slug).count()

        Category.objects.filter(slug=slug).update(todos_count=new_count)


@receiver(m2m_changed, sender=TodoItem.category.through)
def task_cats_removed(sender, instance, action, model, **kwargs):
    #print('action task_cats_removed')
    if action != "post_remove":
        return

    cat_counter = Counter()

    for cat in Category.objects.all():
        cat_counter[cat.slug] = 0

    for t in TodoItem.objects.all():
        for cat in t.category.all():
            cat_counter[cat.slug] += 1

    for slug, new_count in cat_counter.items():
        Category.objects.filter(slug=slug).update(todos_count=new_count)