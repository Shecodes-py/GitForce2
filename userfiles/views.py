from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import CustomUser
from rest_framework import status
from rest_framework import generics 
from .serializers import * 

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from twilio.twiml.messaging_response import MessagingResponse

from rest_framework.permissions import IsAuthenticated

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the userfiles index.")

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Generate JWT token
        tokens = user.tokens()  # to create tokens method in model
        
        return Response({
            "message": "Login successful",
            "user": {
                "email": user.email,
            },
            "tokens": tokens
        }, status=status.HTTP_200_OK)

class RegisterView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True) # this would always run all the methods in the serializer
        user = serializer.save()

        return Response({
            #"id": user.id,
            "message": "User registered successfully",
            "user": {
                "email": user.email,
            }
        }, status=status.HTTP_201_CREATED)

class SaveFileView(generics.CreateAPIView):
    queryset = SavedFile.objects.all()
    serializer_class = SavedFileSerializer
    permission_classes = [AllowAny] # User must be logged in

    def perform_create(self, serializer):
        
        serializer.save(user=self.request.user)

# Endpoint 2: Receive Data (GET)
class UserFilesListView(generics.ListAPIView):
    serializer_class = SavedFileSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Return only the files belonging to the requesting user
        # .order_by('-timestamp') shows newest files first
        return SavedFile.objects.filter(user=self.request.user).order_by('-timestamp')

class UserProfileView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

class CreateFarmerView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # Save user normally; no .user foreign key needed
        serializer.save()

class WhatsAppBotView(APIView):
    # Twilio sends data as form-encoded, so we need these parsers
    parser_classes = [FormParser, MultiPartParser]
    permission_classes = [AllowAny] # Allow Twilio to hit this endpoint without a token

    def post(self, request, *args, **kwargs):
        # 1. Get the data from the request
        incoming_msg = request.data.get('Body', '').strip()
        num_media = request.data.get('NumMedia', '0') # Comes as a string
        sender_number = request.data.get('From')
        
        # 2. Initialize Twilio Response Object
        resp = MessagingResponse()
        msg = resp.message()

        print(f"📩 Message received from {sender_number}")

        # 3. Logic: Check if they sent an image
        if int(num_media) > 0:
            image_url = request.data.get('MediaUrl0')
            
            # --- MOCK AI ANALYSIS START ---
            # In a real scenario, you'd pass 'image_url' to your ML model function here
            print(f"🖼 Analyzing Image: {image_url}")
            
            grade = "Grade A"
            price = "₦12,000"
            token_value = "50 AGRI"
            # --- MOCK AI ANALYSIS END ---

            # 4. Construct the Reply
            reply_text = (
                f"🍅 *AgriTrust Analysis*\n"
                f"----------------\n"
                f"✅ *Quality:* {grade}\n"
                f"💰 *Est. Price:* {price}\n"
                f"----------------\n"
                f"Tap below to mint & sell on Blockchain: 👇\n"
                f"https://your-webapp.com/mint?grade=A&price=12000"
            )
            msg.body(reply_text)
            
        else:
            # Welcome Message (Text only)
            msg.body(
                "👋 Welcome to *AgriTrust Nigeria*!\n\n"
                "Please send a photo 📸 of your crop to get an instant AI valuation."
            )

        # 5. Return XML (Critical for Twilio)
        # We use standard HttpResponse because DRF's Response() returns JSON
        return HttpResponse(str(resp), content_type='text/xml')
    

class FirebaseSyncView(generics.GenericAPIView):
    permission_classes = [AllowAny] # Public, because the user isn't in Django yet
    serializer_class = FirebaseUserSerializer

    def post(self, request):
        email = request.data.get('email')
        
        # 1. Validate that email was sent
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Check if user already exists
        # We use get_or_create. 
        # 'created' is a boolean (True if new user, False if existed)
        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                'username': email, # Use email as username since we don't have one
                'full_name': request.data.get('full_name', ''),
                'farm_location': request.data.get('farm_location', '')
            }
        )

        # 3. If it was a new user, we need to set an unusable password 
        # (Since they login via Firebase, they don't need a Django password)
        if created:
            user.set_unusable_password()
            user.save()
        
        # 4. Generate Django Tokens (So they can make authorized calls later)
        tokens = user.tokens()

        return Response({
            "message": "User synced successfully",
            "created": created, # Tells frontend if this was a new registration
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name
            },
            "tokens": tokens # <--- FRONTEND NEEDS THIS TO SAVE FILES
        }, status=status.HTTP_200_OK)