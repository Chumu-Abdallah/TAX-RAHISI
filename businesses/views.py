from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages 
from django.urls import reverse_lazy
from .models import Business
from .forms import BusinessForm, BusinessUpdateForm

class BusinessListView(LoginRequiredMixin, ListView):
    model = Business
    template_name = 'businesses/list.html'
    paginate_by = 20

    def get_queryset(self):
        return Business.objects.all().select_related('taxpayer')

class BusinessCreateView(LoginRequiredMixin, CreateView):
    model = Business
    form_class = BusinessForm
    template_name = 'businesses/form.html'
    success_url = reverse_lazy('businesses:list')

    def form_valid(self, form):
        resp = super().form_valid(form)
        if form.cleaned_data.get('requests_vat_notice'):
            messages.warning(self.request, "Tahadhari: Mauzo yamevuka 100M, inabidi u-register VAT TRA.")
        else:
            messages.success(self.request, "Biashara Imesajiliwa.")
        return resp

class BusinessUpdateView(LoginRequiredMixin, UpdateView):
    model = Business
    form_class = BusinessUpdateForm
    template_name = 'businesses/form.html'
    success_url = reverse_lazy('businesses:list')

class BusinessDetailView(LoginRequiredMixin, DetailView):
    model = Business
    template_name = 'businesses/detail.html'