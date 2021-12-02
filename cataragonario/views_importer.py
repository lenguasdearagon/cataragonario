
import os
import tempfile
from django.views.generic.base import TemplateView
from linguatec_lexicon.forms import ValidatorForm

from django.core.files.storage import default_storage
from django.shortcuts import redirect
from pathlib import Path

from . import tasks


class ImportMultiVariationValidatorView(TemplateView):
    template_name = "linguatec_lexicon/datavalidator.html"
    title = "Catalan diatopic validator"

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = ValidatorForm(request.POST, request.FILES)

        if form.is_valid():
            xlsx_file = form.cleaned_data['input_file']

            # store uploaded file as a temporal file
            tmp_fd, tmp_file = tempfile.mkstemp(suffix='.xlsx')
            f = os.fdopen(tmp_fd, 'wb')  # open the tmp file for writing
            f.write(xlsx_file.read())  # write the tmp file
            f.close()

            # validate uploaded file and handle errors (if any)
            log_file = self.get_log_filename(tmp_file)
            tasks.run_validator(tmp_file, log_file)

            return redirect("catalan-validator-log", name=log_file)

        context['form'] = form
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'form':  ValidatorForm(),
            'title': self.title,
        })
        return context

    def get_log_filename(self, filename):
        filename = Path(filename).with_suffix('.log')
        filename = default_storage.get_valid_name(filename)
        return default_storage.get_available_name(filename)


class ImportLogView(TemplateView):
    template_name = "cataragonario/import-log-detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': "Import log",
            'output': self.retrieve_log_content(kwargs['name']),
        })
        return context

    def retrieve_log_content(self, filename):
        try:
            content = default_storage.open(filename, mode='r').read()
        except Exception:
            raise
        return content
