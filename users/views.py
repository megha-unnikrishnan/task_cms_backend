


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer, UserSerializer
from rest_framework.permissions import AllowAny
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import RegisterSerializer,PostSerializer,CommentSerializer,LikeSerializer
from .models import CustomUser,Comment,Like,Post
from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponseRedirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.exceptions import PermissionDenied
from .models import CustomUser
from django.contrib.auth.decorators import login_required

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer



class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        # Log detailed errors
        print("Validation errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        




import requests
from django.shortcuts import render, redirect

    
def register_view(request):
    api_url = "http://localhost:8000/api/register/" 
    if request.method == "POST":
        # Get form data from the request
        form_data = {
            "full_name": request.POST.get("full_name"),
            "email": request.POST.get("email"),
            "password": request.POST.get("password"),
            "phone": request.POST.get("phone"),
            "dob": request.POST.get("dob"),
        }

      
        files = {"profile_picture": request.FILES.get("profile_picture")} if "profile_picture" in request.FILES else None

        try:
            response = requests.post(api_url, data=form_data, files=files)
            if response.status_code == 201: 
                
                return redirect("login") 
            else:
                errors = response.json()
                return render(request, "usersview/register.html", {"errors": errors, "form_data": form_data})
        except requests.exceptions.RequestException as e:
            print("API request failed:", e)
            return render(request, "usersview/register.html", {"errors": {"non_field_errors": ["Something went wrong."]}})
    
    # Render the registration page for GET requests
    return render(request, 'usersview/register.html')





def login_view(request):
    api_url = "http://localhost:8000/api/token/" 
    if request.method == "POST":
       
        form_data = {
            "email": request.POST.get("email"),
            "password": request.POST.get("password"),
        }

        try:
           
            response = requests.post(api_url, data=form_data)
            
            if response.status_code == 200:  # Successful login
               
                token_data = response.json()
                access_token = token_data.get("access")
                is_admin = token_data.get("is_admin")  
                print('acces',access_token)
                
                
                request.session['access_token'] = access_token  
                request.session['is_admin'] = is_admin
                if is_admin:
                    return redirect("admin_dashboard_view") 
                else:
                    return redirect("fetch_all_posts") 
            else:
               
                errors = response.json()
                return render(request, "usersview/login.html", {"errors": errors, "form_data": form_data})
        except requests.exceptions.RequestException as e:
            
            print("API request failed:", e)
            return render(request, "usersview/login.html", {"errors": {"non_field_errors": ["Something went wrong."]}})

   
    return render(request, 'usersview/login.html')



def logout_view(request):
    
    request.session.flush()
    
    
    return redirect("login")



@login_required
def user_dashboard_view(request):
    user=request.user
    return render(request, 'usersview/user_dashboard.html',{'user':user})



def createpost(request):
    api_url = "http://localhost:8000/posts/create/" 
    if request.method == "POST":
     
        form_data = {
            "title": request.POST.get("title"),
            "content": request.POST.get("content"),
        }
        files = {"image": request.FILES.get("image")} if "image" in request.FILES else None

        access_token = request.session.get('access_token')

        if not access_token:
            return redirect('login') 
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        try:
            response = requests.post(api_url, data=form_data, files=files, headers=headers)
            
            if response.status_code == 201:  
                return redirect('fetch_all_posts')  
            else:
               
                errors = response.json()
                return render(request, "usersview/createpost.html", {"errors": errors, "form_data": form_data})
        except requests.exceptions.RequestException as e:
         
            print("API request failed:", e)
            return render(request, "usersview/createpost.html", {"errors": {"non_field_errors": ["Something went wrong."]}})

    
    return render(request, 'usersview/createpost.html')


def blog(request):
    return render(request, 'usersview/blog-list.html')


def admin_dashboard_view(request):
    return render(request, 'admin/admin_dashboard.html')

class AdminOnlyView(APIView):
    def get(self, request):
        if not request.user.is_staff:
            return Response({"error": "Only admins are allowed."}, status=status.HTTP_403_FORBIDDEN)
        return Response({"message": "Welcome, Admin!"})


# Create a Post


class PostCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print(f"Logged-in user: {request.user}")

        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(f"Validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostListView(APIView):
    permission_classes = [IsAuthenticated]
    

    def get(self, request):
        if not request.user.is_active:
            return Response({"error": "Your account is inactive. Please contact support."}, status=status.HTTP_403_FORBIDDEN)
        posts = Post.objects.all() 
        serializer = PostSerializer(posts, many=True)  
        return Response(serializer.data) 


from django.http import HttpResponseServerError  
import requests
from django.shortcuts import render, redirect
from django.contrib import messages  # Import messages module

def fetch_posts(request):
    api_url = "http://localhost:8000/posts/"  # URL to fetch posts
    
    # Fetch the access token from session (if available)
    access_token = request.session.get('access_token')
    print('fetchacces', access_token)

    if not access_token:
        return redirect('login')  # Redirect to login if not authenticated
    
    headers = {
        'Authorization': f'Bearer {access_token}'  # Attach the token in the header
    }

    try:
        # Send GET request to fetch posts
        response = requests.get(api_url, headers=headers)

        # Handle successful response
        if response.status_code == 200:
            posts = response.json()  # Parse the JSON response
            print("Fetched posts:", posts)
            return render(request, 'usersview/demo.html', {'posts': posts})

        # Handle error responses from the API
        elif response.status_code == 403:
            messages.error(request, "Your account is inactive. Please contact support.")  # Use messages.error to display error
            return redirect('login')

        elif response.status_code == 404:
            messages.error(request, "Posts not found.")  # Use messages.error for 404 error
            return render(request, 'usersview/demo.html')

        else:
            errors = response.json()  # Parse the error response
            messages.error(request, errors.get("error", "An unknown error occurred."))
            return render(request, 'usersview/demo.html')

    except requests.exceptions.RequestException as e:
        # Handle any request-related exceptions
        print("API request failed:", e)
        messages.error(request, "Something went wrong. Please try again later.")  # Use messages.error for request failure
        return render(request, 'usersview/demo.html')

def post_detail(request, id):
    api_url = f"http://localhost:8000/api/posts/{id}/"  # URL to fetch a single post
    access_token = request.session.get('access_token')
    if not access_token:
        return redirect('login')  

    headers = {
        'Authorization': f'Bearer {access_token}' 
    }

    try:
        response = requests.get(api_url, headers=headers)
        print('respones',response)
        if response.status_code == 200:
            post = response.json() 
            print('respones',post)
            
            return render(request, 'usersview/post_detail.html', {'post': post})
        else:
            errors = response.json()
            return render(request, 'usersview/post_detail.html', {'errors': errors})

    except requests.exceptions.RequestException as e:
        print("API request failed:", e)
        return render(request, 'usersview/post_detail.html', {'errors': {'non_field_errors': ['Something went wrong.']}})



from django.shortcuts import render, redirect
import requests

class PostDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            serializer = PostSerializer(post)
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response({"detail": "Post not found"}, status=404)


from django.shortcuts import get_object_or_404


class PostUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk, *args, **kwargs):
        try:
            post = Post.objects.get(pk=pk, author=request.user)
        except Post.DoesNotExist:
            return Response({"error": "Post not found or you do not have permission to edit this post."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PostDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        try:
            post = Post.objects.get(pk=pk, author=request.user)
            post.delete()
            return Response({"message": "Post deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response({"error": "Post not found or you do not have permission to delete this post."}, status=status.HTTP_404_NOT_FOUND)



from django.contrib import messages
def deletepost(request, pk):
    api_url = f"http://localhost:8000/posts/{pk}/delete/"
    access_token = request.session.get('access_token')
    if not access_token:
        return redirect('login')

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    try:
        response = requests.delete(api_url, headers=headers)
        if response.status_code == 204:
            messages.success(request, "Post deleted successfully.")
        else:
            error_message = response.json().get("detail", "Failed to delete the post.")
            messages.error(request, error_message)
    except requests.exceptions.RequestException as e:
        print("API request failed:", e)
        messages.error(request, "An error occurred while trying to delete the post.")

    return redirect('fetch_all_posts')







# Like a Post
class PostLikeView(generics.CreateAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def create(self, request, *args, **kwargs):
        post_id = self.kwargs.get('pk')
        post = Post.objects.get(id=post_id)
        user = request.user
        
        # Ensure a user can like a post only once
        if Like.objects.filter(post=post, user=user).exists():
            return Response({"detail": "You have already liked this post"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create like
        like = Like.objects.create(post=post, user=user)
        post.likes_count += 1
        post.save()
        return Response(self.get_serializer(like).data, status=status.HTTP_201_CREATED)

# Unlike a Post
class PostUnlikeView(generics.DestroyAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def perform_destroy(self, instance):
        instance.post.likes_count -= 1
        instance.post.save()
        super().perform_destroy(instance)

# Get Comments for a Post

class PostCommentListView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.kwargs.get('pk')
        return Comment.objects.filter(post_id=post_id)

    def perform_create(self, serializer):
        post_id = self.kwargs.get('pk')
        post = Post.objects.get(id=post_id)
        serializer.save(post=post, author=self.request.user)



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            
            refresh_token = request.headers.get('Authorization').split(' ')[1]  # Extract token from 'Bearer <token>'

            if not refresh_token:
                return Response({"detail": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

            
            token = RefreshToken(refresh_token)

            
            token.blacklist()

            return Response({"detail": "Successfully logged out"}, status=status.HTTP_200_OK)

        except TokenError:
            return Response({"detail": "Invalid token or already blacklisted"}, status=status.HTTP_400_BAD_REQUEST)
        




from django.http import JsonResponse
def post_edit_delete(request, post_id):
    api_url = f"http://localhost:8000/editdeleteapi/{post_id}/"
    access_token = request.session.get('access_token')
    
    if not access_token:
        return redirect('login')  

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Check if the method is PUT or DELETE from the form
    method = request.POST.get('method', None)

    if method == 'PUT':
        updated_data = {
            'title': request.POST.get('title'),
            'content': request.POST.get('content')
        }

        try:
            response = requests.put(api_url, headers=headers, json=updated_data)
            if response.status_code == 200:
                post = response.json() 
                return render(request, 'usersview/post_detail.html', {'post': post})
            else:
                errors = response.json()
                return render(request, 'usersview/post_detail.html', {'errors': errors})

        except requests.exceptions.RequestException as e:
            print("API request failed:", e)
            return render(request, 'usersview/post_detail.html', {'errors': {'non_field_errors': ['Something went wrong.']}})

    elif method == 'DELETE':
        try:
            response = requests.delete(api_url, headers=headers)
            if response.status_code == 200:
                return redirect('post_list')  
            else:
                errors = response.json()
                return render(request, 'usersview/post_detail.html', {'errors': errors})

        except requests.exceptions.RequestException as e:
            print("API request failed:", e)
            return render(request, 'usersview/post_detail.html', {'errors': {'non_field_errors': ['Something went wrong.']}})

    else:
        # Handle invalid request methods (if necessary)
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    




from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import requests







def update_post(request, pk):
    api_url = f"http://localhost:8000/posts/{pk}/update/"
    access_token = request.session.get('access_token')

    if not access_token:
        return redirect('login')

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    if request.method == "POST":
        form_data = {
            "title": request.POST.get("title"),
            "content": request.POST.get("content"),
        }
        files = {"image": request.FILES.get("image")} if "image" in request.FILES else None

        try:
            response = requests.put(api_url, data=form_data, files=files, headers=headers)

            if response.status_code == 200:  
                messages.success(request, "Post updated successfully!")
                return redirect('fetch_all_posts')  
            else:
                errors = response.json()
                return render(request, "usersview/post_edit.html", {"errors": errors, "form_data": form_data, "post_id": pk})
        except requests.exceptions.RequestException as e:
            print("API request failed:", e)
            messages.error(request, "Something went wrong while updating the post.")
            return render(request, "usersview/post_edit.html", {"errors": {"non_field_errors": ["Something went wrong."]}, "form_data": form_data, "post_id": pk})

    # GET request: Fetch the existing post data
    try:
        response = requests.get(f"http://localhost:8000/api/posts/{pk}/", headers=headers)
        if response.status_code == 200:
            post_data = response.json()
            return render(request, 'usersview/post_edit.html', {"form_data": post_data, "post_id": pk})
        else:
            return render(request, "usersview/post_edit.html", {"errors": {"non_field_errors": ["Post not found."]}})
    except requests.exceptions.RequestException as e:
        print("API request failed:", e)
        return render(request, "usersview/post_edit.html", {"errors": {"non_field_errors": ["Something went wrong."]}})
    


def comments(request, pk):
    api_url = f"http://localhost:8000/posts/{pk}/comments/"
    access_token = request.session.get('access_token')

    if not access_token:
        return redirect('login')

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    if request.method == "POST":
        form_data = {
            "content": request.POST.get("content"),
        }

        # Check if content is provided
        if not form_data["content"]:
            errors = {"content": ["This field is required."]}
            # Fetch existing comments to display them along with errors
            comments_response = requests.get(api_url, headers=headers)
            comments_data = comments_response.json() if comments_response.status_code == 200 else []
            return render(request, "usersview/demo.html", {"errors": errors, "comments": comments_data, "post_id": pk})

        try:
            response = requests.post(api_url, json=form_data, headers=headers)  # Use json instead of data

            if response.status_code == 201:  # Comment created successfully
                return redirect('comments', pk=pk)  # Redirect to the same comments page
            else:
                errors = response.json()
                # Fetch existing comments to display them along with errors
                comments_response = requests.get(api_url, headers=headers)
                comments_data = comments_response.json() if comments_response.status_code == 200 else []
                return render(request, "usersview/demo.html", {"errors": errors, "comments": comments_data, "post_id": pk})
        except requests.exceptions.RequestException as e:
            print("API request failed:", e)
            return render(request, "usersview/demo.html", {"errors": {"non_field_errors": ["Something went wrong."]}, "post_id": pk})

    # GET request: Fetch existing comments
    try:
        response = requests.get(api_url, headers=headers)
        comments_data = response.json() if response.status_code == 200 else []
        return render(request, "usersview/demo.html", {"comments": comments_data, "post_id": pk})
    except requests.exceptions.RequestException as e:
        print("API request failed:", e)
        return render(request, "usersview/demo.html", {"errors": {"non_field_errors": ["Something went wrong."]}, "post_id": pk})