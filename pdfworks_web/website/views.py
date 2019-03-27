import os
import zipfile
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.db.models import Case, When
from django.http.response import HttpResponse
from django.shortcuts import render, redirect

from .lib.pdfworks_lib.pdfworks import Converter

from .models import RequestFiles, UploadedFile


def homepage(request):
    return redirect('merge/')


def merge(request):
    def merge_lib_call(input_files_list, output_filename):
        converter = Converter()
        output = os.path.join('output', '%s.pdf' % output_filename)
        converter.convert(input_files_list, output)
        return output

    if request.method == "POST":
        if 'order_array' in request.POST:
            try:
                request_files_object = RequestFiles.objects.get(csrf_id=request.POST['csrfmiddlewaretoken'])
                if 'order_array' not in request.POST:
                    raise ObjectDoesNotExist
            except ObjectDoesNotExist:
                return HttpResponse("You haven't uploaded any files")
            if request_files_object:
                print("request object is: %s" % request_files_object)
                order_array = request.POST['order_array'].split(',')
                preserved = Case(*[When(uuid=uuid, then=pos) for pos, uuid in enumerate(order_array)])
                files_objects = request_files_object.uploaded_files.filter(uuid__in=order_array).order_by(preserved)
                files_list = [file.filename.name for file in files_objects]
                print(files_list)
                filesys_output_filename = merge_lib_call(files_list, request_files_object.csrf_id)
                with open(filesys_output_filename, 'rb') as file_to_send:
                    response = HttpResponse(file_to_send, 'text/html')
                    if request.POST['output_filename'] != '':
                        save_filename = "%s.pdf" % request.POST['output_filename']
                    else:
                        save_filename = "pdfWorks.org_%s.pdf" % request_files_object.csrf_id[:8]
                    response['Content-Disposition'] = 'attachment; filename="%s"' % save_filename
                    request_files_object.delete(output_filename=filesys_output_filename)
                return response
        else:
            try:
                request_files_object = RequestFiles.objects.get(csrf_id=request.POST['csrfmiddlewaretoken'])
            except ObjectDoesNotExist:
                request_files_object = RequestFiles(csrf_id=request.POST['csrfmiddlewaretoken'], tool_type='merge')
                request_files_object.save()
            uploaded_file = UploadedFile(request_session=request_files_object)
            uploaded_file.filename.save(str(request.FILES['file']), ContentFile(request.FILES['file'].read()))
            uploaded_file.uuid = request.POST['file_uuid']
            uploaded_file.save()
            print("csrf_id: %s" % request_files_object.csrf_id)
            print("file uploaded: %s with uuid: %s" % (uploaded_file.filename, uploaded_file.uuid))
    return render(request,
                  'website/merge.html',
                  {'section': 'merge'})


def split(request):
    def split_lib_call(filename, csrf_id):
        output_dir = os.path.join('output', csrf_id)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        converter = Converter()
        converter.split_pdf(filename, output_dir)
        zipf = zipfile.ZipFile(os.path.join(output_dir, '%s.zip' % csrf_id), 'w', zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(os.path.join(settings.BASE_DIR, output_dir)):
            for file in files:
                if file.endswith('.pdf'):
                    zipf.write(
                        os.path.join(output_dir, file),
                        os.path.relpath(os.path.join(output_dir, file), output_dir)
                    )
        zipf.close()
        return zipf.filename

    if request.method == "POST":
        if request.is_ajax():
            try:
                request_files_object = RequestFiles.objects.get(csrf_id=request.POST['csrfmiddlewaretoken'])
            except ObjectDoesNotExist:
                request_files_object = RequestFiles(csrf_id=request.POST['csrfmiddlewaretoken'], tool_type='split')
                request_files_object.save()
                print("new object created with sid %s" % request_files_object.csrf_id)
            print("csrf_id: %s" % request_files_object.csrf_id)
            uploaded_filename = str(request.FILES['file'])
            uploaded_file = UploadedFile(request_session=request_files_object)
            uploaded_file.filename.save(uploaded_filename, ContentFile(request.FILES['file'].read()))
            uploaded_file.save()
            uploaded_filename = uploaded_file.filename.name
            output_filename = split_lib_call(uploaded_filename, request_files_object.csrf_id)
            print("zip: %s" % output_filename)
        else:
            request_files_object = RequestFiles.objects.get(csrf_id=request.POST['csrfmiddlewaretoken'])
            output_filepath = os.path.join(
                'output',
                os.path.join(
                    request_files_object.csrf_id,
                    "%s.zip" % request_files_object.csrf_id
                )
            )
            filename = request_files_object.uploaded_files.all()[0].filename.name
            print("output_filepath is %s" % output_filepath)
            print("filename is %s" % os.path.basename(filename))
            with open(output_filepath, 'rb') as file_to_send:
                response = HttpResponse(file_to_send, 'text/html')
                save_filename = "%s_pdfWorks.org.zip" % filename
                response['Content-Disposition'] = 'attachment; filename="%s"' % save_filename
                request_files_object.delete(output_filename=os.path.join('output', request_files_object.csrf_id))
            return response

    return render(request,
                  'website/split.html',
                  {'section': 'split'})
