from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect

urlpatterns = [
	url(r'^login/$',views.LogIn),
	url(r'^logout/$',views.Logout),
	url(r'^login-submit/$',views.LogInSubmit),
	url(r'^home/$',views.Home),
	url(r'^get-response/$',views.GetResponse),
	url(r'^fetch-flight/$',views.FetchFlight),
	url(r'^book-flight/$',views.BookFlight),
	url(r'^previous-booked/$',views.PreviousBooked),

]