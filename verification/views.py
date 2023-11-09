from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
import pyotp
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import phoneModel
import base64


class generateKey:
    @staticmethod
    def returnValue(phone):
        return str(phone) + str(datetime.date(datetime.now())) + "Some Random Secret Key"


class getPhoneNumberRegistered(APIView):
    @staticmethod
    def get(request, phone):
        try:
            Mobile = phoneModel.objects.get(Mobile=phone)  
        except ObjectDoesNotExist:
            phoneModel.objects.create(
                Mobile=phone,
            )
            Mobile = phoneModel.objects.get(Mobile=phone)  
        Mobile.counter += 1  
        Mobile.save()  
        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(phone).encode())  
        OTP = pyotp.HOTP(key)  
        print(OTP.at(Mobile.counter))
        return Response({"OTP": OTP.at(Mobile.counter)}, status=200)  


    @staticmethod
    def post(request, phone):
        try:
            Mobile = phoneModel.objects.get(Mobile=phone)
        except ObjectDoesNotExist:
            return Response("User does not exist", status=404)  

        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(phone).encode())  
        OTP = pyotp.HOTP(key)  
        if OTP.verify(request.data["otp"], Mobile.counter):  
            Mobile.isVerified = True
            Mobile.save()
            return Response("You are authorised", status=200)
        return Response("OTP is wrong", status=400)


# Time-based
EXPIRY_TIME = 50 # this is in seconds

class getPhoneNumberRegistered_TimeBased(APIView):
    @staticmethod
    def get(request, phone):
        try:
            Mobile = phoneModel.objects.get(Mobile=phone)  
        except ObjectDoesNotExist:
            phoneModel.objects.create(
                Mobile=phone,
            )
            Mobile = phoneModel.objects.get(Mobile=phone)  
        Mobile.save()  
        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(phone).encode())  
        OTP = pyotp.TOTP(key,interval = EXPIRY_TIME)  
        print(OTP.now())
        return Response({"OTP": OTP.now()}, status=200) 

    @staticmethod
    def post(request, phone):
        try:
            Mobile = phoneModel.objects.get(Mobile=phone)
        except ObjectDoesNotExist:
            return Response("User does not exist", status=404)  

        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(phone).encode())  
        OTP = pyotp.TOTP(key,interval = EXPIRY_TIME)  
        if OTP.verify(request.data["otp"]):  
            Mobile.isVerified = True
            Mobile.save()
            return Response("You are authorised", status=200)
        return Response("OTP is wrong/expired", status=400)
