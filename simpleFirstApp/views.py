from django.contrib import messages
from django.core import serializers
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail, EmailMessage
from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import Context
from django.template.loader import get_template
from django.utils.html import escape
from xhtml2pdf import pisa
from io import StringIO, BytesIO

from simpleDjangoProject.settings import EMAIL_HOST_USER
from .models import Students, Teachers, Courses, StudentSubjects, Subjects
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required

# Create your views here.

def FirstPageController(request):
    return HttpResponse("<h1>My First Django Project Page</h1>")

def IndexPageController(request):
    return HttpResponseRedirect("/homePage")

def HtmlPageController(request):
    return render(request,"htmlpage.html")

def HtmlPageControllerWithData(request):
    data1="This is Data 1 Passing to HTML Page"
    data2="This is Data 2 Passing to HTML Page"
    return render(request,"htmlpage_with_data.html",{'data':data1,'data1':data2})

def PassingDatatoController(request,url_data):
    return HttpResponse("<h2>This is Data Coming Via URL : "+url_data)

@login_required(login_url="/login_user/")
def addData(request):
    courses=Courses.objects.all()
    return render(request,"add_data.html",{'courses':courses})

@login_required(login_url="/login_user/")
def add_student(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Now Allowed</h2>")
    else:
        file=request.FILES['profile']
        fs=FileSystemStorage()
        profile_img=fs.save(file.name,file)
        try:
            course=Courses.objects.get(id=request.POST.get('course',''))
            student=Students(name=request.POST.get('name',''),email=request.POST.get('email',''),standard=request.POST.get('standard',''),hobbies=request.POST.get('hobbies',''),roll_no=request.POST.get('roll_no',''),bio=request.POST.get('bio',''),profile_image=profile_img,course=course)
            student.save()


            subject_list=request.POST.getlist('subjects[]')
            for subject in subject_list:
                subj=Subjects.objects.get(id=subject)
                student_subject=StudentSubjects(subject_id=subj,student_id=student)
                student_subject.save()
            messages.success(request,"Added Successfully")
        except Exception as e:
            print(e)
            messages.error(request,"Failed to Add Student")

        return HttpResponseRedirect("/addData")

@login_required(login_url="/login_user/")
def add_teacher(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Now Allowed</h2>")
    else:
        try:
            teacher=Teachers(name=request.POST.get('name',''),email=request.POST.get('email',''),department=request.POST.get('department',''))
            teacher.save()
            messages.success(request,"Added Successfully")
        except:
            messages.error(request,"Failed to Add Teacher")

        return HttpResponseRedirect("/addData")

@login_required(login_url="/login_user/")
def show_all_data(request):
    all_teacher=Teachers.objects.all()
    all_student=Students.objects.all()

    return render(request,"show_data.html",{'students':all_student,'teachers':all_teacher})

@login_required(login_url="/login_user/")
def delete_student(request,student_id):
    student=Students.objects.get(id=student_id)
    student.delete()
    messages.error(request, "Deleted Successfully")
    return HttpResponseRedirect("/show_all_data")

@login_required(login_url="/login_user/")
def update_student(request,student_id):
    student=Students.objects.get(id=student_id)
    if student==None:
        return HttpResponse("Student Not Found")
    else:
        return render(request,"student_edit.html",{'student':student})

@login_required(login_url="/login_user/")
def edit_student(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        student=Students.objects.get(id=request.POST.get('id',''))
        if student==None:
            return HttpResponse("<h2>Student Not Found</h2>")
        else:
            if request.FILES.get('profile')!=None:
                file = request.FILES['profile']
                fs = FileSystemStorage()
                profile_img = fs.save(file.name, file)
            else:
                profile_img=None

            if profile_img!=None:
                student.profile_image=profile_img

            student.name=request.POST.get('name','')
            student.email=request.POST.get('email','')
            student.standard=request.POST.get('standard','')
            student.hobbies=request.POST.get('hobbies','')
            student.roll_no=request.POST.get('roll_no','')
            student.bio=request.POST.get('bio','')
            student.save()

            messages.success(request,"Updated Successfully")
            return HttpResponseRedirect("update_student/"+str(student.id)+"")


def LoginUser(request):
    if request.user==None or request.user =="" or request.user.username=="":
        return render(request,"login_page.html")
    else:
        return HttpResponseRedirect("/homePage")

def RegisterUser(request):
    if request.user==None:
        return render(request,"register_page.html")
    else:
        return HttpResponseRedirect("/homePage")

def SaveUser(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        username=request.POST.get('username','')
        email=request.POST.get('email','')
        password=request.POST.get('password','')

        if not (User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists()):
            User.objects.create_user(username,email,password)
            messages.success(request,"User Created Successfully")
            return HttpResponseRedirect('/register_user')
        else:
            messages.error(request,"Email or Username Already Exist")
            return HttpResponseRedirect('/register_user')

def DoLoginUser(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed")
    else:
        username=request.POST.get('username','')
        password=request.POST.get('password','')
        user=authenticate(username=username,password=password)
        login(request,user)

        if user!=None:
            return HttpResponseRedirect('/homePage')
        else:
            messages.error(request,"Invalid Login Details")
            return HttpResponseRedirect('/login_user')

@login_required(login_url="/login_user/")
def HomePage(request):
    return render(request,"home_page.html")

def LogoutUser(request):
    logout(request)
    request.user=None
    return HttpResponseRedirect("/login_user")

def testStudent(request):
    student=Students.objects.all()
    student_obj=serializers.serialize('python',student)
    return JsonResponse(student_obj,safe=False)

def SendPlainEmail(request):
    message=request.POST.get('message','')
    subject=request.POST.get('subject','')
    mail_id=request.POST.get('email','')
    email=EmailMessage(subject,message,EMAIL_HOST_USER,[mail_id])
    email.content_subtype='html'
    email.send()
    return HttpResponse("Sent")

def send_mail_plain_with_stored_file(request):
    message=request.POST.get('message','')
    subject=request.POST.get('subject','')
    mail_id=request.POST.get('email','')
    email=EmailMessage(subject,message,EMAIL_HOST_USER,[mail_id])
    email.content_subtype='html'

    file=open("README.md","r")
    file2=open("manage.py","r")
    email.attach("README.md",file.read(),'text/plain')
    email.attach("manage.py",file2.read(),'text/plain')

    email.send()
    return HttpResponse("Sent")


def send_mail_plain_with_file(request):
    message = request.POST.get('message', '')
    subject = request.POST.get('subject', '')
    mail_id = request.POST.get('email', '')
    email = EmailMessage(subject, message, EMAIL_HOST_USER, [mail_id])
    email.content_subtype = 'html'

    file = request.FILES['file']
    email.attach(file.name, file.read(), file.content_type)

    email.send()
    return HttpResponse("Sent")

def setSession(request):
    request.session['session_data_1']="This is Session 1 Data"
    request.session['session_data_2']="This is Session 2 Data"
    return HttpResponse("Session Set")

def view_session(request):
    if request.session.has_key("session_data_1"):
        session_data_1=request.session['session_data_1']
    else:
        session_data_1="Data is Blank"

    if request.session.has_key("session_data_2"):
        session_data_2=request.session['session_data_2']
    else:
        session_data_2="Data is Blank"

    return render(request,"show_session_data.html",{"session_data_1":session_data_1,"session_data_2":session_data_2})

def del_session(request):
    del request.session['session_data_1']
    del request.session['session_data_2']
    return HttpResponse("Session Deleted")

def getPdfPage(request):
    all_student=Students.objects.all()
    data={'students':all_student}
    template=get_template("pdf_page.html")
    data_p=template.render(data)
    response=BytesIO()

    pdfPage=pisa.pisaDocument(BytesIO(data_p.encode("UTF-8")),response)
    if not pdfPage.err:
        return HttpResponse(response.getvalue(),content_type="application/pdf")
    else:
        return HttpResponse("Error Generating PDF")

def ShowChatHome(request):
    return render(request,"chat_home.html")

def ShowChatPage(request,room_name,person_name):
    return render(request,"chat_screen.html",{'room_name':room_name,'person_name':person_name})
    #return HttpResponse("Chat page "+room_name+""+person_name)