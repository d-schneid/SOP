from abc import ABCMeta, abstractmethod

from typing import Optional, List, Dict, Type

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
    the admin site.
    """
    class Meta:
        abstract = True

    @abstractmethod
    def get_admin_add_form(self) -> Type[ModelForm[Model]]:
        """
        Return a Form class for use in the admin add view. This is used by add_view.
        """
        pass

    @abstractmethod
    def get_admin_change_form(self) -> Type[ModelForm[Model]]:
        """
        Return a Form class for use in the admin change view. This is used by
        change_view.
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Return the name of the associated model.
        """
        pass

    # override to get current user in form
    def get_form(self, request: HttpRequest, *args, **kwargs) -> Type[ModelForm[Model]]:
        form = super().get_form(request, *args, **kwargs)
        form.current_user = request.user  # type: ignore
        return form

    # remove inlines from add_view
    def get_inline_instances(self,
                             request: HttpRequest,
                             obj: Optional[Model] = None
    ) -> List[InlineModelAdmin]:
        """
        :return: The inline instances that belong to the selected object.
        """
        return obj and super().get_inline_instances(request, obj) or []

    def add_view(self,
                 request: HttpRequest,
                 form_url: str = "",
                 extra_context: Optional[Dict[str, object]] = None
    ) -> HttpResponse:
        """
        Encapsulates the logic for adding a new object.

        After adding a new object, it redirects back to the change list.
        """
        self.form = self.get_admin_add_form()
        return super().add_view(request, form_url, extra_context)

    def change_view(self,
                    request: HttpRequest,
                    object_id: str,
                    form_url: str = "",
                    extra_context: Optional[Dict[str, object]] = None
    ) -> HttpResponse:
        """
        Encapsulates the logic for editing the selected object.

        After editing the selected object, it redirects back to the change list.
        """
        self.form = self.get_admin_change_form()
        return super().change_view(request, object_id, form_url, extra_context)

    # adjust behavior of deletion of model
    def delete_view(
            self,
            request: HttpRequest,
            object_id: str,
            extra_context: Optional[Dict[str, object]] = None,
    ) -> HttpResponse:
        """
        Encapsulates the logic for deleting the selected object and checking if it can
        be deleted.

        If the selected object can be  deleted, it displays a confirmation page.

        Next, it deletes the selected object and redirects back to the change list.
        """
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