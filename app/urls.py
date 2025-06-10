from django.urls import path
from rest_framework.routers import DefaultRouter
from django.urls import include
from .views import (
    RegisterView, UserProfileDetailView, UserProfileCreateView,home,
    DiabeticProfileCreateView,DiabeticProfileDetailView,DiabeticProfileListView,
    UserMealViewSet,
    OwnerDashboardView,
    recommend_calories, DailyCalorieSummaryView,
    ReminderListCreateView,
    SendReminderView,
    UserContactListView,
    OperatorReportView,
    DietRecommendationListCreateView,
    DietRecommendationDetailView,
    UserDietRecommendationListView
    
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,   # View to obtain JWT access and refresh tokens (login)
    TokenRefreshView,     # View to refresh access token using refresh token
    TokenBlacklistView,   # View to blacklist a refresh token (logout)
)

router = DefaultRouter()

#LogMeals API endpoint
router.register(r'logmeals', UserMealViewSet, basename='user-meals')

urlpatterns = [

    path('', include(router.urls)), 

    path('home',home, name='home'),  # Home page view
    # User registration endpoint (signup)
    path('signup/', RegisterView.as_view(), name='signup'),

    # JWT login endpoint - returns access and refresh tokens after user credentials verified
    path('login/', TokenObtainPairView.as_view(), name='login'),

    # Refresh JWT access token endpoint using a valid refresh token
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Logout endpoint to blacklist the refresh token, effectively logging out user
    path('logout/', TokenBlacklistView.as_view(), name='logout'),

    # Retrieve, update, or delete the logged-in user's profile details
    path('profile/', UserProfileDetailView.as_view(), name='user-profile'),

    # Create user profile endpoint (for logged-in users)
    path('profile/create/', UserProfileCreateView.as_view(), name='create-user-profile'),

     # Create diabetic profile
    path('diabetic-reports/', DiabeticProfileListView.as_view(), name='diabetic-reports-list'),
    path('diabetic-reports/create/', DiabeticProfileCreateView.as_view(), name='diabetic-reports-create'),
    path('diabetic-reports/<int:pk>/', DiabeticProfileDetailView.as_view(), name='diabetic-reports-detail'),


    # #Calorie recommendation endpoint
    path('recommend-calories/', recommend_calories, name='recommend_calories'),
    ######calorie tracking ########
    path('daily-calorie-summary/', DailyCalorieSummaryView.as_view(), name='daily_calorie_summary'),

 



    ####################### ACTORS IN SYSTEM #######################
    path('owner/', OwnerDashboardView.as_view(), name='owner-dashboard'),


    ########################Operator APIs########################
    # Operator - Create or List patient reminders
    path("operator/reminders/", ReminderListCreateView.as_view(), name="reminder-list-create"),
    
    # Operator - Manually send reminder email to a patient
    path("operator/reminders/send/<int:pk>/", SendReminderView.as_view(), name="send-reminder"),        
    
    # Operator - View all users' contact details
    path("operator/users/contacts/", UserContactListView.as_view(), name="user-contacts"),
    
    # Operator - Generate basic user and reminder reports
    path("operator/reports/", OperatorReportView.as_view(), name="operator-report"),
    ##################################################################################################

    ###########Nutritionist APIs########################
    path('nutritionist/diet-recommendations/', DietRecommendationListCreateView.as_view(), name='nutritionist-diet-recommendations'),
    path('nutritionist/diet-recommendations/<int:pk>/', DietRecommendationDetailView.as_view(), name='diet-recommendation-detail'),

    #User Diet Recommendations
    path('user/diet-recommendations/', UserDietRecommendationListView.as_view(), name='user-diet-recommendations'),
]



        

    

