from django.urls import path
from boutique import views 
from django.contrib import admin  
from django.conf import settings
from django.conf.urls.static import static

app_name = 'boutique'

urlpatterns = [
     path('', views.home, name='home'),
    # Produits
    path('produits/', views.liste_produits, name='liste_produits'),
    path('produit/<int:produit_id>/', views.detail_produit, name='detail_produit'),
    
    # Panier
    path('panier/', views.gestion_panier, name='gestion_panier'),
    path('panier/ajouter/<int:produit_id>/', views.ajouter_au_panier, name='ajouter_panier'),
    path('panier/retirer/<int:ligne_id>/', views.retirer_du_panier, name='retirer_panier'),
    
    # Commandes
    path('commande/passer/', views.passer_commande, name='passer_commande'),
    path('commande/<int:commande_id>/', views.suivi_commande, name='suivi_commande'),
    
    # Paiement
    path('paiement/<int:commande_id>/', views.paiement, name='paiement'),
    
    # Avis
    path('produit/<int:produit_id>/avis/', views.laisser_avis, name='laisser_avis'),

    # Autres pages
    path('about/', views.about_us, name='about_us'),
    path('contact/', views.contact_us, name='contact_us'),
    
    # Administration
    path('admin/', admin.site.urls),  # Ajouter cette ligne pour l'admin Django
   

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

