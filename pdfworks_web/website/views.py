import os
import shutil

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.http.response import HttpResponse
from django.shortcuts import render

from .lib.pdfworks_lib.pdfworks import Converter

from .models import RequestFiles, UploadedFile



def homepage(request):
    return render(request,
                  'website/homepage.html',
                  {'section': 'merge'})


def merge(request):
    def merge_lib_call(input_files_list, output_filename):
        converter = Converter()
        output = f"output/{output_filename}.pdf"
        converter.convert(input_files_list, output)
        return output

    if request.method == "POST":
        if 'submit' in request.POST:
            try:
                request_files_object = RequestFiles.objects.get(csrf_id=request.POST['csrfmiddlewaretoken'])
            except ObjectDoesNotExist:
                return HttpResponse("You haven't uploaded any files")
            if request_files_object:
                print(f"request object is: {request_files_object}")
                files_objects = request_files_object.uploaded_files.all()
                files_list = [file.filename.name for file in files_objects]
                print(files_list)
                output_filename = merge_lib_call(files_list, request_files_object.csrf_id)
                with open(output_filename, 'rb') as file_to_send:
                    response = HttpResponse(file_to_send, 'application/x-gzip')
                    # response['Content-Length'] = file_to_send.size
                    response['Content-Disposition'] = f'attachment; filename="{request_files_object.csrf_id}.pdf"'
                    shutil.rmtree(f'uploads/{request_files_object.csrf_id}')
                    os.remove(output_filename)
                    request_files_object.delete()
                return response
        else:
            try:
                request_files_object = RequestFiles.objects.get(csrf_id=request.POST['csrfmiddlewaretoken'])
            except ObjectDoesNotExist:
                request_files_object = RequestFiles(csrf_id=request.POST['csrfmiddlewaretoken'])
                request_files_object.save()
                print(f"new object created with sid {request_files_object.csrf_id}")
            print(f"csrf_id: {request_files_object.csrf_id}")
            uploaded_file = UploadedFile(request_session=request_files_object)
            uploaded_file.filename.save(str(request.FILES['file']), ContentFile(request.FILES['file'].read()))
            uploaded_file.save()
    return render(request,
                  'website/merge.html',
                  {'section': 'merge'})


def split(request):
    def split_lib_call():
        converter = Converter()
        converter.split_pdf()

    if request.method == "POST":
        if 'submit' in request.POST:
            try:
                request_files_object = RequestFiles.objects.get(csrf_id=request.POST['csrfmiddlewaretoken'])
            except ObjectDoesNotExist:
                return HttpResponse("You haven't uploaded any files")
            if request_files_object:
                print(f"request object is: {request_files_object}")
                files_list = [file.filename.name for file in request_files_object.uploaded_files.all()]
                print(files_list)
                # request_files_object.delete()
                return HttpResponse(f"It's okay, files: {files_list}")
        else:
            try:
                request_files_object = RequestFiles.objects.get(csrf_id=request.POST['csrfmiddlewaretoken'])
            except ObjectDoesNotExist:
                request_files_object = RequestFiles(csrf_id=request.POST['csrfmiddlewaretoken'])
                request_files_object.save()
                print(f"new object created with sid {request_files_object.csrf_id}")
            print(f"csrf_id: {request_files_object.csrf_id}")
            uploaded_file = UploadedFile(request_session=request_files_object)
            uploaded_file.filename.save(str(request.FILES['file']), ContentFile(request.FILES['file'].read()))
            uploaded_file.save()

    return render(request,
                  'website/split.html',
                  {'section': 'split'})


def offline(request):
    return render(request,
                  'website/offline.html',
                  {'section': 'offline'})
