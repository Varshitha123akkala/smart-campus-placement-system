from django.urls import path

from . import views

urlpatterns = [path("index.html", views.index, name="index"),
               path("CompanyLogin.html", views.CompanyLogin, name="CompanyLogin"),	      
               path("CompanyLoginAction", views.CompanyLoginAction, name="CompanyLoginAction"),
               path("RegisterAction", views.RegisterAction, name="RegisterAction"),
               path("Register.html", views.Register, name="Register"),
               path("TPOLoginAction", views.TPOLoginAction, name="TPOLoginAction"),
               path("TPOLogin.html", views.TPOLogin, name="TPOLogin"),
	       path("StudentLogin.html", views.StudentLogin, name="StudentLogin"),
	       path("StudentLoginAction", views.StudentLoginAction, name="StudentLoginAction"),
	       path("CompanyLogin.html", views.CompanyLogin, name="CompanyLogin"),
               path("CompanyLoginAction", views.CompanyLoginAction, name="CompanyLoginAction"),
	       path("PostJob", views.PostJob, name="PostJob"),
               path("PostJobAction", views.PostJobAction, name="PostJobAction"),	   
	       path("AddQuestion", views.AddQuestion, name="AddQuestion"),
	       path("AddQuestionAction", views.AddQuestionAction, name="AddQuestionAction"),
	       path("ViewPerformance", views.ViewPerformance, name="ViewPerformance"),
	       path("ViewFeedback", views.ViewFeedback, name="ViewFeedback"),
	       path("UpdateProfile", views.UpdateProfile, name="UpdateProfile"),
	       path("UpdateProfileAction", views.UpdateProfileAction, name="UpdateProfileAction"),
	       path("Recommendation", views.Recommendation, name="Recommendation"),	       
	       path("ModifyProfileAction", views.ModifyProfileAction, name="ModifyProfileAction"),

	       path("JobStatus", views.JobStatus, name="JobStatus"),	   
	       path("Feedback", views.Feedback, name="Feedback"),
	       path("FeedbackAction", views.FeedbackAction, name="FeedbackAction"),
	       path("ApplyJob", views.ApplyJob, name="ApplyJob"),
	       path("ExamTestAction", views.ExamTestAction, name="ExamTestAction"),
          path('chatbot/', views.chatbot, name='chatbot'),
path('chatbot_api/', views.chatbot_api, name='chatbot_api'),
path('ViewPlacementCompanyWise', views.ViewPlacementCompanyWise, name='ViewPlacementCompanyWise'),
path('FutureDrivesAnnouncement', views.FutureDrivesAnnouncement, name='FutureDrivesAnnouncement'),
]

