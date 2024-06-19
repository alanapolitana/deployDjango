from django.apps import AppConfig

class MyComicAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'MyComicApp'



    def ready(self):
        import MyComicApp.load_initial_data
        
        import MyComicApp.signals
