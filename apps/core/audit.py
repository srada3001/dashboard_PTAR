"""Admin pages that leave an AuditEntry for every creation, change and deletion, with the values
before and after (Django's own admin log only says which fields changed)."""

import datetime

from django import forms
from django.contrib import admin
from django.forms.models import InlineForeignKeyField

from .models import AuditEntry

# Never stored, not even hashed: the log only says the password was set.
SECRET_FIELDS = {"password", "password1", "password2"}
# Formset bookkeeping, not data.
FORMSET_FIELDS = {"id", "DELETE", "ORDER"}


def display(field, value):
    """A form value as people read it: names instead of ids, labels instead of choice keys."""
    if value is None or value == "" or value == []:
        return ""
    if isinstance(field, forms.ModelMultipleChoiceField):
        pks = [getattr(item, "pk", item) for item in value]
        return ", ".join(sorted(str(obj) for obj in field.queryset.model._default_manager.filter(pk__in=pks)))
    if isinstance(field, forms.ModelChoiceField):
        if not hasattr(value, "pk"):
            value = field.queryset.model._default_manager.filter(pk=value).first()
        return str(value) if value is not None else ""
    if isinstance(value, bool):
        return "Sí" if value else "No"
    if isinstance(field, forms.ChoiceField):
        return str(dict(field.choices).get(value, value))
    if isinstance(value, datetime.date):
        return value.isoformat()
    return str(value)


def describe_form(form, change):
    """{label: [before, after]} for the fields a form changed (or filled, when creating)."""
    if change:
        names = form.changed_data
    else:
        names = [name for name in form.fields if form.cleaned_data.get(name) not in (None, "", [])]
    changes = {}
    for name in names:
        if name in SECRET_FIELDS or name in FORMSET_FIELDS or name not in form.fields:
            continue
        field = form.fields[name]
        if isinstance(field, InlineForeignKeyField):
            continue
        before = display(field, form.get_initial_for_field(field, name)) if change else ""
        after = display(field, form.cleaned_data.get(name))
        if before != after:
            changes[str(field.label or name)] = [before, after]
    return changes


def describe_formset(formset):
    """Rows added, changed or removed in an inline, keyed by the row: {"Alias «BA4010»": [...]}."""
    label = str(formset.model._meta.verbose_name).capitalize()
    changes = {}
    for form in formset.forms:
        deleted = form in formset.deleted_forms
        if not hasattr(form, "cleaned_data") or (not form.has_changed() and not deleted):
            continue
        if deleted:
            if form.instance.pk:
                changes[f"{label} «{form.instance}»"] = ["presente", "quitado"]
        elif form.instance.pk is None:
            changes[f"{label} «{form.instance}»"] = ["", "agregado"]
        else:
            for key, values in describe_form(form, change=True).items():
                changes[f"{label} «{form.instance}» · {key}"] = values
    return changes


class AuditedAdmin(admin.ModelAdmin):
    """ModelAdmin that records an AuditEntry after saving (main form + inlines) and before deleting."""

    def save_model(self, request, obj, form, change):
        request._audit_changes = describe_form(form, change)
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        request._audit_changes.update(describe_formset(formset))
        super().save_formset(request, form, formset, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        changes = getattr(request, "_audit_changes", {})
        if change and not changes:
            return
        action = AuditEntry.Action.UPDATE if change else AuditEntry.Action.CREATE
        AuditEntry.record(request.user, action, form.instance, changes)

    def delete_model(self, request, obj):
        AuditEntry.record(request.user, AuditEntry.Action.DELETE, obj)
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            AuditEntry.record(request.user, AuditEntry.Action.DELETE, obj)
        super().delete_queryset(request, queryset)
