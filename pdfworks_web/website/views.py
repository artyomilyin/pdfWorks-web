import hashlib
import os
import zipfile
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.db.models import Case, When
from django.http.response import HttpResponse
from django.shortcuts import render

from .lib.pdfworks_lib.pdfworks import Converter

from .models import RequestFiles, UploadedFile, Statistic


def homepage(request):
    # just show a homepage
    return render(request,
                  'website/homepage.html',
                  {'section': 'homepage'})


def merge(request):
    def merge_lib_call(input_files_list, output_filename):
        converter = Converter()
        output = os.path.join('output', '%s.pdf' % output_filename)
        converter.convert(input_files_list, output)
        return output

    if request.method == "POST":
        # order_array is filled via javascript on client's side and determines an order for files to be converted/merged
        # also presence of order_array variable in POST shows that there was a form submission (not AJAX)
        if 'order_array' in request.POST:
            # get related RequestFiles object (it contains all the uploaded files)
            try:
                # use csrf token as an identifier
                request_files_object = RequestFiles.objects.get(csrf_id=request.POST['csrfmiddlewaretoken'])
                if 'order_array' not in request.POST:
                    raise ObjectDoesNotExist
            except ObjectDoesNotExist:
                return HttpResponse("You haven't uploaded any files")
            if request_files_object:
                print("request object is: %s" % request_files_object)
                order_array = request.POST['order_array'].split(',')

                # define an order of files and the final list of files
                preserved = Case(*[When(uuid=uuid, then=pos) for pos, uuid in enumerate(order_array)])
                files_objects = request_files_object.uploaded_files.filter(uuid__in=order_array).order_by(preserved)
                files_list = [file.filename.name for file in files_objects]
                print(files_list)

                # get the name of output file
                filesys_output_filename = merge_lib_call(files_list, request_files_object.csrf_id)
                # create an http response with the file an send it to the client
                with open(filesys_output_filename, 'rb') as file_to_send:
                    response = HttpResponse(file_to_send, 'text/html')
                    if request.POST['output_filename'] != '':
                        save_filename = "%s.pdf" % request.POST['output_filename']
                    else:
                        save_filename = "pdfWorks.org_%s.pdf" % request_files_object.csrf_id[:8]
                    response['Content-Disposition'] = 'attachment; filename="%s"' % save_filename
                    request_files_object.delete(output_filename=filesys_output_filename)
                    # add a statistics record
                    Statistic.objects.create(output_filename=save_filename,
                                             tool_type='merge',
                                             ip_address=request.META.get('HTTP_X_REAL_IP', 'unknown')).save()
                return response
        else:
            # means that it is not a form submission and files are still uploading
            # get related object or create one if it does not exist yet, use csrf token as an identifier
            try:
                request_files_object = RequestFiles.objects.get(csrf_id=request.POST['csrfmiddlewaretoken'])
            except ObjectDoesNotExist:
                request_files_object = RequestFiles(csrf_id=request.POST['csrfmiddlewaretoken'], tool_type='merge')
                request_files_object.save()
            # add new uploaded file to RequestFiles object
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
    def split_lib_call(filename, unq_dir):
        """
        A function to use pdfworks-lib's split method and to zip pages into an archive.
        Returns the name of the zip file.
        """
        output_dir = os.path.join('output', unq_dir)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        converter = Converter()
        converter.split_pdf(filename, output_dir)

        # create a zip file
        zipf = zipfile.ZipFile(os.path.join(output_dir, '%s.zip' % unq_dir), 'w', zipfile.ZIP_DEFLATED)
        # add all the files from split's output to this zip file
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
            # means files are still uploading
            file_uuid = request.POST['file_uuid']
            file_csrf = request.POST['csrfmiddlewaretoken']

            # create an instance of RequestFiles model
            unq_file_id = hashlib.sha1(("%s%s" % (file_uuid, file_csrf)).encode('utf-8')).hexdigest()
            request_files_object = RequestFiles(csrf_id=unq_file_id, tool_type='split')
            request_files_object.save()
            # created a related instance of UploadedFile model
            uploaded_file = UploadedFile(request_session=request_files_object)
            uploaded_file.filename.save(str(request.FILES['file']), ContentFile(request.FILES['file'].read()))
            uploaded_file.save()
            uploaded_filename = uploaded_file.filename.name
            # split the file and get a zip-archive
            output_filename = split_lib_call(uploaded_filename, request_files_object.csrf_id)
            # zip is ready to be sent to the client
            print("zip: %s" % output_filename)
        else:
            # means there was a form submition from javascript and we can serve the file to the client
            file_uuid = request.POST['file_uuid']
            file_csrf = request.POST['csrfmiddlewaretoken']
            # define which zip to send
            unq_file_id = hashlib.sha1(("%s%s" % (file_uuid, file_csrf)).encode('utf-8')).hexdigest()
            request_files_object = RequestFiles.objects.get(csrf_id=unq_file_id)
            uploaded_file = request_files_object.uploaded_files.first()
            output_filepath = os.path.join('output', os.path.join(unq_file_id, "%s.zip" % unq_file_id))
            filename = os.path.basename(uploaded_file.filename.name)
            # open zip file and return it to the client
            with open(output_filepath, 'rb') as file_to_send:
                response = HttpResponse(file_to_send, 'text/html')
                save_filename = "%s_pdfWorks.org.zip" % filename
                response['Content-Disposition'] = 'attachment; filename="%s"' % save_filename
                request_files_object.delete(output_filename=os.path.join('output', request_files_object.csrf_id))
                # add a statistics record
                Statistic.objects.create(output_filename=save_filename,
                                         tool_type='split',
                                         ip_address=request.META.get('HTTP_X_REAL_IP', 'unknown')).save()
            return response

    return render(request,
                  'website/split.html',
                  {'section': 'split'})
