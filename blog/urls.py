from rest_framework import routers

from blog.views import PostViewSet, CommentViewSet, FeedViewSet

router = routers.DefaultRouter()
router.register("posts", PostViewSet, basename="posts")
router.register("comments", CommentViewSet, basename="comments")
router.register("feed", FeedViewSet, basename="feed")

urlpatterns = router.urls

app_name = "blog"
