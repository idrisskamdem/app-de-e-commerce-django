from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Configuration pour l'utilisateur personnalisé
class UtilisateurAdmin(UserAdmin):
    model = Utilisateur
    list_display = ('username', 'email', 'adresse', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('email', 'adresse', 'photo_profil')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )

# Configuration des proxy models
@admin.register(Client)
class ClientAdmin(UtilisateurAdmin):
    list_display = ('username', 'email', 'adresse', 'date_joined')
    list_filter = ('date_joined',)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_staff=False)

@admin.register(Admin)
class AdminAdmin(UtilisateurAdmin):
    list_display = ('username', 'email', 'is_superuser')
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_staff=True)

# Configuration pour les produits
class LignePanierInline(admin.TabularInline):
    model = LignePanier
    extra = 0

class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prix', 'stock', 'categorie', 'est_disponible')
    list_filter = ('categorie',)
    search_fields = ('nom', 'description')
    prepopulated_fields = {'slug': ('nom',)} if 'slug' in Produit.__dict__ else {}

# Configuration pour les commandes
class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0

class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'date_commande', 'statut', 'total_commande')
    list_filter = ('statut', 'date_commande')
    inlines = [LigneCommandeInline]
    
    def total_commande(self, obj):
        return obj.calculer_total()

# Configuration pour le panier
class PanierAdmin(admin.ModelAdmin):
    list_display = ('client', 'nombre_articles', 'total_panier')
    inlines = [LignePanierInline]
    
    def nombre_articles(self, obj):
        return obj.lignepanier_set.count()
    
    def total_panier(self, obj):
        return obj.calculer_total()

# Configuration des autres modèles

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('get_commande_id', 'montant', 'statut')
    
    def get_commande_id(self, obj):
        return obj.commande.id

class AvisAdmin(admin.ModelAdmin):
    list_display = ('produit', 'client', 'note', 'date')
    search_fields = ('produit__nom', 'client__username')

class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'nombre_produits')
    search_fields = ('nom',)
    
    def nombre_produits(self, obj):
        return obj.produits.count()

# Enregistrement des modèles
admin.site.register(Utilisateur, UtilisateurAdmin)
admin.site.register(Categorie, CategorieAdmin)
admin.site.register(Produit, ProduitAdmin)
admin.site.register(Panier, PanierAdmin)
admin.site.register(Commande, CommandeAdmin)
admin.site.register(Avis, AvisAdmin)
