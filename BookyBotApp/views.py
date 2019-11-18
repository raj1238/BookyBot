from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from BookyBotApp.models import *
# from BookyBotApp.utils import *

from django.shortcuts import render, HttpResponse, get_object_or_404
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required

# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.views import APIView
# from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.paginator import Paginator

import requests
import json
import os
import uuid

from chatterbot import ChatBot
from textblob import TextBlob
from textblob import classifiers
from chatterbot.trainers import ChatterBotCorpusTrainer
import json
import pandas as pd

from . import extract_info
from . import flight_api
from . import extraction_json

df = pd.read_csv(os.getcwd()+'/BookyBotApp/flightdata.csv')

training = [
    ("I do not want help", "neg"),
    ("May be next time", "neg"),
    ("I don't think so", "neg"),
    ("I need no help", "neg"),
    ("Not needed", "neg"),
    ("Nope", "neg"),
    ("yes", "pos"),
    ("Sure", "pos"),
    ("I would like that", "pos"),
    ("Yes, I need help", "pos"),
    ("I am in need of help", "pos"),
    ("I don't want your help", "neg"),
    ("I think I am fine on my own", "neg"),
    ("In need of help", "pos"),
    ("No its okay", "neg")
]
classifier = classifiers.NaiveBayesClassifier(training)

class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return

# Create your views here.
@login_required(login_url='/login/')
def Home(request):
    booky_bot_user = BookyBotUser.objects.get(username=request.user.username)
    booky_bot_user.step_counter=0
    booky_bot_user.trail_flag=0
    booky_bot_user.v_destination=""
    booky_bot_user.v_source=""
    booky_bot_user.v_date=""
    booky_bot_user.save()
    return render(request, 'home.html')

@login_required(login_url='/login/')
def Logout(request):
    logout(request)
    return HttpResponseRedirect('/login/')

def LogIn(request):
    return render(request, 'login.html')

class LogInSubmitAPI(APIView):

    authentication_classes = (
           CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

       response = {}
       response['status'] = 500
       try:

           data = request.data

           username = data['username']
           password = data['password']

           user = authenticate(username=username, password=password)

           login(request, user)

           booky_bot_user = BookyBotUser.objects.get(username=username)
           booky_bot_user.step_counter=0
           booky_bot_user.trail_flag=0
           booky_bot_user.v_destination=""
           booky_bot_user.v_source=""
           booky_bot_user.v_date=""
           #arr_temp = []
           booky_bot_user.save()


           response['status'] = 200

       except Exception as e:
           print("Error LogInSubmitAPI", str(e))

       return Response(data=response)

class GetResponseAPI(APIView):

    authentication_classes = (
           CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

       response = {}
       response['status'] = 500
       try:

            data = request.data
            userText = data["user-msg"]
            booky_bot_user = BookyBotUser.objects.get(username=request.user.username)
            bookings = Booking.objects.filter(user=booky_bot_user)
            #print(bookings)
            blob = TextBlob(userText, classifier=classifier)
            
            if (blob.classify()=="pos" and len(bookings)!=0 and booky_bot_user.v_destination == "" and booky_bot_user.v_source == ""):
                booking = bookings.all().last()
                flight_details = json.loads(booking.flight_details)
                booky_bot_user.v_source = flight_details["flight_details"][6]
                booky_bot_user.v_destination = flight_details["flight_details"][7]

            if booky_bot_user.v_date == "" and booky_bot_user.v_destination == "" and booky_bot_user.v_source == "":    
                
                arr_temp = extract_info.blob_search(userText)
                booky_bot_user.v_destination=arr_temp[1]
                booky_bot_user.v_source=arr_temp[0]
                booky_bot_user.v_date=arr_temp[2]

            if booky_bot_user.v_source == "":
                
                #response['bot-msg']="Enter source city"
                
                if source_dest_check(userText,df) == True:
                    booky_bot_user.v_source = userText
                    print(booky_bot_user.v_source)

                else:
                    arr_1 = extract_info.blob_search(userText)
                    booky_bot_user.v_source = arr_1[0]

            elif booky_bot_user.v_destination == "":
                #response['bot-msg'] = "Enter destination city"
                if source_dest_check(userText,df) == True:
                    booky_bot_user.v_destination = userText
                else:
                    arr_1 = extract_info.blob_search(userText)
                    booky_bot_user.v_destination = arr_1[1]
            elif booky_bot_user.v_date == "":
                #response['bot-msg'] = "Enter date of travel"
                arr_1 = extract_info.blob_search(userText)
                booky_bot_user.v_date = arr_1[2]
            
            

            if booky_bot_user.v_source == "":
                response['bot-msg']="Enter source city"
            elif booky_bot_user.v_destination == "":
                response['bot-msg']="Enter destination city"
            elif booky_bot_user.v_date == "":
                response['bot-msg']="Enter travel date"
            elif booky_bot_user.v_date != "" and booky_bot_user.v_destination != "" and booky_bot_user.v_source != "":
                if booky_bot_user.v_source == booky_bot_user.v_destination:
                    booky_bot_user.v_source = ""
                    booky_bot_user.v_destination = ""
                    response['bot-msg'] = 'Source city and destination city are same. Please enter valid source city.'
                else:
                    response['bot-msg'] = 'Fetching options'

            # print(userText)
            # blob_text = TextBlob(userText, classifier=classifier)

            # booky_bot_user = BookyBotUser.objects.get(username=request.user.username)
            # booky_bot_user.step_counter=booky_bot_user.step_counter+1
            # #booky_bot_user.save()
        

            # #print(booky_bot_user.step_counter)
            # if (booky_bot_user.step_counter == 1):
            #     if(blob_text.classify() == "pos"):
            #         booky_bot_user.trail_flag=1
            #         response['bot-msg']="Do you want to book  a ticket?"
            #     else:
            #         booky_bot_user.trail_flag=0
            #         response['bot-msg']='Okay. You can always say "Help Me" if you need my assistance.'
                

            # if(booky_bot_user.trail_flag==1):
            #     if(booky_bot_user.step_counter==2):
            #         if (blob_text.classify() == "pos"):
            #             response['bot-msg']="Enter city name from where you want to travel."
            #         else:
            #             booky_bot_user.trail_flag = 0
            #             response['bot-msg']='Okay. You can always say "Help Me" if you need my assistance.'
            #     elif(booky_bot_user.step_counter==3):
            #         print(source_dest_check(userText,df))
            #         if source_dest_check(userText,df) == True:
            #             booky_bot_user.v_source = str(userText).lower()
            #             response['bot-msg']='Enter destination city where you want to go'
            #         else:
            #             booky_bot_user.step_counter = booky_bot_user.step_counter - 1
            #             response['bot-msg']='Enter a valid source city'
            #     elif(booky_bot_user.step_counter==4):
            #         if source_dest_check(userText,df) == True:
            #             booky_bot_user.v_destination = str(userText).lower()
            #             response['bot-msg']='Enter travel date'
            #         else:
            #             booky_bot_user.step_counter = booky_bot_user.step_counter - 1
            #             response['bot-msg']="Enter a valid destination City"
            #     elif(booky_bot_user.step_counter==5):
            #         booky_bot_user.v_date = userText
            #         #api_integration(source,destination,date)
            #         response['bot-msg']="Fetching options"
            #     elif(booky_bot_user.step_counter==6):
            #         if (blob_text.classify() == "neg"):
            #             response['bot-msg']="Thank You for using our service. Come next time."

            # elif(booky_bot_user.trail_flag==0 and booky_bot_user.step_counter!=1):
            #     if (booky_bot_user.step_counter!=8 and booky_bot_user.step_counter!=9):
            #         print("First If",booky_bot_user.step_counter)
            #         arr_temp = extract_info.blob_search(userText)
            #         print(arr_temp)
            #         if all(''==s or s.isspace() for s in arr_temp):
            #             booky_bot_user.step_counter = 2
            #             booky_bot_user.trail_flag = 1
            #             response['bot-msg']='Enter city from where you want to travel.'
            #         elif(arr_temp[0]=='' and arr_temp[1]==''):
            #             booky_bot_user.step_counter = 3
            #             booky_bot_user.trail_flag = 1
            #             booky_bot_user.v_destination = arr_temp[0]
            #             response['bot-msg']='Enter city where you want to go'
            #         elif(arr_temp[1]=='' and arr_temp[2]==''):
            #             booky_bot_user.step_counter = 3
            #             booky_bot_user.trail_flag = 1
            #             booky_bot_user.v_destination = arr_temp[0]
            #             response['bot-msg']='Enter city where you want to go'
            #         elif(arr_temp[0]=='' and arr_temp[2]==''):
            #             booky_bot_user.step_counter = 3
            #             booky_bot_user.trail_flag = 1
            #             booky_bot_user.v_source = arr_temp[1]
            #             response['bot-msg']='Enter city from where you want to travel.'
            #         elif(arr_temp[0]==''):
            #             booky_bot_user.v_destination = arr_temp[1]
            #             booky_bot_user.v_date = arr_temp[2]
            #             booky_bot_user.step_counter = 7
            #             booky_bot_user.trail_flag = 0
            #             response['bot-msg']='Enter city from where you want to travel.'
            #         elif(arr_temp[1]==''):
            #             booky_bot_user.v_source = arr_temp[0]
            #             booky_bot_user.v_date = arr_temp[2]
            #             booky_bot_user.step_counter = 8
            #             booky_bot_user.trail_flag = 0
            #             response['bot-msg']='Enter city where you want to go.'
            #         elif(arr_temp[2]==''):
            #             booky_bot_user.v_source = arr_temp[0]
            #             booky_bot_user.v_destination = arr_temp[1]
            #             booky_bot_user.step_counter = 4
            #             booky_bot_user.trail_flag = 1
            #             response['bot-msg']='Enter travel date'
            #         elif not any(''==s or s.isspace() for s in arr_temp):
            #             booky_bot_user.v_source = arr_temp[0]
            #             booky_bot_user.v_destination = arr_temp[1]
            #             booky_bot_user.v_date = arr_temp[2]
            #             response['bot-msg']='Fetching options'
            #     else:
            #         print("Else",booky_bot_user.step_counter)
            #         if(booky_bot_user.step_counter==8):
            #             booky_bot_user.v_source = userText
            #             response['bot-msg']="Fetching options"
            #         if(booky_bot_user.step_counter==9):
            #             booky_bot_user.v_destination = userText
            #             response['bot-msg']="Fetching options"



            booky_bot_user.save()
            print(booky_bot_user.v_source)
            print(booky_bot_user.v_destination)
            print(booky_bot_user.v_date)
            print(response['bot-msg'])
            response['status'] = 200

       except Exception as e:
           print("Error GetResponseAPI", str(e))

       return Response(data=response)

class FetchFlightAPI(APIView):
    authentication_classes = (
           CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

       response = {}
       response['status'] = 500
       try:


            booky_bot_user = BookyBotUser.objects.get(username=request.user.username)
            
            if booky_bot_user.v_source == booky_bot_user.v_destination:
                response1 = {}
                response1["flight_detail"] = "no"
                json_response = json.dumps(response1)
                response["flight_detail"]=json_response #think better logic for this
            else:
               
                src_code = df.loc[df['City'] == booky_bot_user.v_source.lower()]['Code'].iloc[0]
                dest_code = df.loc[df['City'] == booky_bot_user.v_destination.lower()]['Code'].iloc[0]
                date = booky_bot_user.v_date
                list_sorted =  flight_api.parse_my(src_code, dest_code, date)
                #list_sorted = sorted(list_sorted, key=lambda k: k['ticket price'], reverse=False)
                print(list_sorted[len(list_sorted)-1]['error'])
                if (list_sorted[len(list_sorted)-1]['error']=="failed to process the page"):
                    response["flag"] = "unsuccessful"
                    booky_bot_user.v_date=""
                    booky_bot_user.v_source=""
                    booky_bot_user.v_destination=""
                    booky_bot_user.save()
                else:
                    flight_details = extraction_json.flight_data(list_sorted)
                    print(flight_details)
                    response1 = {}
                    response1["flight_detail"] = flight_details
                    json_response = json.dumps(response1)
                    print(list_sorted[:7])
                    response["flight_detail"]=json_response
                    response["flag"] = "successful"
        #return flight_details
            
            response['status'] = 200

       except Exception as e:
           print("Error FetchFlightAPI", str(e))

       return Response(data=response)
def source_dest_check(city,df):
    city = str(city).lower()
    list1 = df['City'].to_list()
    if city in list1:
        return True
    else:
        return False

class BookFlightAPI(APIView):
    authentication_classes = (
           CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = request.data
            booky_bot_user = BookyBotUser.objects.get(username=request.user.username)
            source = booky_bot_user.v_source
            destination = booky_bot_user.v_destination
            date = booky_bot_user.v_date
      
            flight_details = json.loads(data["flight_detail"])
            
            flight_details.append(str(source).title())
            flight_details.append(str(destination).title())
            flight_details.append(date)

            booky_bot_user.v_source=""
            booky_bot_user.v_destination=""
            booky_bot_user.v_date=""
            booky_bot_user.save()



            json_flight_details = {
                "flight_details" : flight_details,
            }
            

            booking = Booking.objects.create(user=booky_bot_user, flight_details=json.dumps(json_flight_details))
            #userText = json.loads(data["flight_detail"])
            #print(userText)

            response["status"] = 200

        except Exception as e:
            print("Error BookFlightAPI", str(e))

        return Response()

class PreviousBookedAPI(APIView):
    authentication_classes = (
           CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

       response = {}
       response['status'] = 500
       try:

            booky_bot_user = BookyBotUser.objects.get(username=request.user.username)
            if Booking.objects.filter(user=booky_bot_user).exists():
                bookings = Booking.objects.filter(user=booky_bot_user)
                booked_flights = []
                for booking in bookings:
                    flight = booking.flight_details
                    flight=json.loads(flight)

                    booked_flights.append(flight['flight_details'])
                
                json_bookings = {}
                json_bookings["bookings"] = booked_flights
                response["bookings"] = json.dumps(json_bookings)

            response['status'] = 200

       except Exception as e:
           print("Error PreviousBookedAPI", str(e))

       return Response(data=response)

LogInSubmit = LogInSubmitAPI.as_view()
GetResponse = GetResponseAPI.as_view()
FetchFlight = FetchFlightAPI.as_view()
BookFlight = BookFlightAPI.as_view()
PreviousBooked = PreviousBookedAPI.as_view()

