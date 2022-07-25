from abc import ABCMeta, abstractmethod

from typing import Optional

from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponse
from django.contrib.admin.actions import delete_selected as django_delete_selected
from django.db.models import QuerySet


class AbstractModelAdminMeta(ABCMeta, type(admin.ModelAdmin)):
    pass


class AbstractModelAdmin(admin.ModelAdmin, metaclass=AbstractModelAdminMeta):
    class Meta:
        abstract = True

    @abstractmethod
    def get_admin_add_form(self):
        pass

    @abstractmethod
    def get_admin_change_form(self):
        pass

    @abstractmethod
    def get_model_name(self):
        pass

    # override to get current user in form
    def get_form(self, request, *args, **kwargs):
        form = super().get_form(request, *args, **kwargs)
        form.current_user = request.user  # type: ignore
        return form

    # remove inlines from add_view
    def get_inline_instances(self, request, obj=None):
        return obj and super().get_inline_instances(request, obj) or []

    def add_view(self, request, form_url="", extra_context=None):
        self.form = self.get_admin_add_form()
        return super().add_view(request, form_url, extra_context)

    def change_view(
            self,
            request: HttpRequest,
            object_id: str,
            form_url="",
            extra_context: Optional[dict[str, object]] = None,
    ):
        self.form = self.get_admin_change_form()
        return super().change_view(request, object_id, form_url, extra_context)

    # adjust behavior of deletion of model
    def delete_view(
            self,
            request: HttpRequest,
            object_id: str,
            extra_context: Optional[dict[str, object]] = None,
    ) -> HttpResponse:
        instance = self.get_object(request, object_id)
        if instance is None:
            return

        if instance.experiment_set.count() > 0:  # type: ignore
            messages.error(request,
                           f"This {self.get_model_name()} cannot be deleted, "
                           "since it is used in at least one experiment (see below)"
                           )
            return self.change_view(request, object_id, "", extra_context)
        return super().delete_view(request, object_id, extra_context)

    # adjust behavior of deletion of queryset
    def delete_selected(self, request: HttpRequest, obj: QuerySet):
        instances = obj.all()
        for instance in instances:
            if instance.experiment_set.count() > 0:  # type: ignore
                messages.error(request,
                               "Bulk deletion cannot be executed, " \
                               f"since at least {self.get_model_name()} {instance.display_name} "
                               "is used in at least one experiment"
                               )
                return
        return django_delete_selected(self, request, instances)