from django.shortcuts import render, get_object_or_404, redirect
from .forms import *
from .models import FAQ, FAQSection
import datetime
from django.contrib.auth.models import Group, User
from dashboard.decorators import *

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def landing(request):

    context = {
    }

    return render(request, "visit_and_faq/home.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def add_faq_section(request):
    form = FAQSectionForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('faq_test')
    else:
        form = FAQSectionForm(request.POST or None)

    context = {
        'form': form,
        'title': "Add FAQ Section",
        'page_title': "Add FAQ Section",
    }

    return render(request, "visit_and_faq/add_edit_comm.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def add_faq(request, sec_id):
    form = FAQForm(request.POST or None)
    section = FAQSection.objects.get(pk=sec_id)

    if form.is_valid():
        form.save()
        section.questions.add(FAQ.objects.latest('id'))
        return redirect('faq_test')
    else:
        form = FAQForm(request.POST or None)

    context = {
        'form': form,
        'title': "Add FAQ",
        'page_title': "Add FAQ",
        'section': section.name
    }

    return render(request, "visit_and_faq/add_edit_comm.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def edit_faq(request, faq_id):
    faq = FAQ.objects.get(pk=faq_id)
    form = FAQForm(request.POST or None, instance=faq)
    if form.is_valid():
        form.save()
        return redirect('faq_test')
    else:
        form = FAQForm(request.POST or None, instance=faq)

    context = {
        'form': form,
        'title': "Edit FAQ",
        'page_title': "Edit FAQ",

    }

    return render(request, "visit_and_faq/add_edit_comm.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def delete_faq(request, faq_id):
    faq = get_object_or_404(FAQ, pk=faq_id)
    faq.delete()

    return redirect('faq_test')

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def add_visitor_instr(request):
    form = VisitorInstructionForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('visitor_instructions')
    else:
        form = VisitorInstructionForm(request.POST or None)

    context = {
        'form': form,
        'title': "Add Visit Instruction",
        'page_title': "Add Visit Instruction",
    }

    return render(request, "visit_and_faq/add_edit_comm.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def edit_visitor_instr(request, instr_id):
    instr = VisitorInstruction.objects.get(pk=instr_id)
    form = VisitorInstructionForm(request.POST or None, instance=instr)
    if form.is_valid():
        form.save()
        return redirect('visitor_instructions')
    else:
        form = VisitorInstructionForm(request.POST or None, instance=instr)

    context = {
        'form': form,
        'title': "Edit Visit Instruction",
        'page_title': "Edit Visit Instruction",
    }

    return render(request, "visit_and_faq/add_edit_comm.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def delete_visitor_instr(request, instr_id):
    instr = get_object_or_404(VisitorInstruction, pk=instr_id)
    instr.delete()

    return redirect('visitor_instructions')
