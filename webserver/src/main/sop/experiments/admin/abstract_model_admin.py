from abc import ABCMeta, abstractmethod

from typing import Optional

from django.contrib import admin, messages
from django.contrib.admin.options import InlineModelAdmin
from django.http import HttpRequest, HttpResponse
from django.contrib.admin.actions import delete_selected as django_delete_selected
from django.db.models import QuerySet, Model
from django.template.response import TemplateResponse
from django.forms import ModelForm


class AbstractModelAdminMeta(ABCMeta, type(admin.ModelAdmin)):
    pass


class AbstractModelAdmin(admin.ModelAdmin, metaclass=AbstractModelAdminMeta):
    """
    An abstract class that encapsulates functionality for checks before deletion
    processes and the application of concrete views for models that are registered in
    the admin interface.
    """
    class Meta:
        abstract = True

    @abstractmethod
    def get_admin_add_form(self) -> type[ModelForm[Model]]:
        """
        Hook for specifying custom admin add forms.
        @return: The Form class for use in the admin add view. This is used by
        add_view.
        """
        raise NotImplementedError

    @abstractmethod
    def get_admin_change_form(self) -> type[ModelForm[Model]]:
        """
        Hook for specifying custom admin change forms.
        @return: The Form class for use in the admin change view. This is used by
        change_view.
        """
        raise NotImplementedError

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Hook for specifying custom model names.
        @return: The name of the associated model of this model admin.
        """
        raise NotImplementedError

    # override to get current user in form
    def get_form(self, request: HttpRequest, *args, **kwargs) -> type[ModelForm[Model]]:
        form = super().get_form(request, *args, **kwargs)
        form.current_user = request.user  # type: ignore
        return form

    # remove inlines from add_view
    def get_inline_instances(self,
                             request: HttpRequest,
                             obj: Optional[Model] = None
                             ) -> list[InlineModelAdmin]:
        """
        Fetches the inline instances of the given object.

        @param request: The HTTPRequest, this will be given by django.
        @param obj: If any, the model instance of which the inline instances shall be
        returned.
        @return: If an object was given, a list of the inline instances that belong to
        the given object. Otherwise, an empty list.
        """
        return obj and super().get_inline_instances(request, obj) or []

    def add_view(self,
                 request: HttpRequest,
                 form_url: str = "",
                 extra_context: Optional[dict[str, object]] = None
                 ) -> HttpResponse:
        """
        View for the model instance addition page in the admin interface.
        After adding a new model instance, it redirects back to the change list.

        @param request: The HTTPRequest, this will be given by django.
        @param form_url: The URL of the form that shall be used for the add view.
        @param extra_context: Additional information that shall be presented by the
        add view.
        @return: A redirect to the change list.
        """
        self.form = self.get_admin_add_form()
        return super().add_view(request, form_url, extra_context)

    def change_view(self,
                    request: HttpRequest,
                    object_id: str,
                    form_url: str = "",
                    extra_context: Optional[dict[str, object]] = None
                    ) -> HttpResponse:
        """
        The view for editing a selected object.
        After editing the selected object, it redirects back to the change list.

        @param request: The HTTPRequest, this will be given by django.
        @param object_id: The primary key of the object that shall be edited.
        @param form_url: The URL of the form that shall be used for the add view.
        @param extra_context: Additional information that shall be presented by the
        change view.
        @return: A redirect to the change list.
        """
        self.form = self.get_admin_change_form()
        return super().change_view(request, object_id, form_url, extra_context)

    # adjust behavior of deletion of model
    def delete_view(
            self,
            request: HttpRequest,
            object_id: str,
            extra_context: Optional[dict[str, object]] = None,
    ) -> Optional[HttpResponse]:
        """
        The view for deleting a selected object. Also checks if the selected object can
        be deleted.
        If the selected object can be deleted, it displays a confirmation page.
        Next, it deletes the selected object and redirects back to the change list.

        @param request: The HTTPRequest, this will be given by django.
        @param object_id: The primary key of the object that shall be deleted.
        @param extra_context: Additional information that shall be presented by the
        delete view.
        @return: A redirect to the change list.
        """
        instance = self.get_object(request, object_id)
        if instance is None:
            return None

        if instance.experiment_set.count() > 0:  # type: ignore
            messages.error(request,
                           f"This {self.get_model_name()} cannot be deleted, "
                           "since it is used in at least one experiment (see below)"
                           )
            return self.change_view(request, object_id, "", extra_context)
        return super().delete_view(request, object_id, extra_context)

    # adjust behavior of deletion of queryset
    def delete_selected(self,
                        request: HttpRequest,
                        obj: QuerySet
                        ) -> Optional[TemplateResponse]:
        """
        Default action which deletes the selected objects.
        This action first displays a confirmation page which shows all the deletable
        objects, or, if the user has no permission one of the related
        childs (foreignkeys), a "permission denied" message.
        Next, it deletes all selected objects and redirects back to the change list.

        @param request: The HTTPRequest, this will be given by django.
        @param obj: The selected objects that shall be deleted.
        @return: A redirect to the change list.
        """
        instances = obj.all()
        for instance in instances:
            if instance.experiment_set.count() > 0:  # type: ignore
                messages.error(request,
                               "Bulk deletion cannot be executed, "
                               f"since at least {self.get_model_name()} "
                               f"{instance.display_name} "
                               "is used in at least one experiment"
                               )
                return None
        return django_delete_selected(self, request, instances)
